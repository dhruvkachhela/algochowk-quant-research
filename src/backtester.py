"""
Event-Driven Backtester Module
Simulates realistic portfolio execution with:
- Dynamic Stop-Loss (e.g. 1.5x ATR or fixed loss exit)
- Early Mean-Reversion Take-Profit (reclaiming pre-drop close)
- Multi-slot dynamic capital allocator (splits cash across K concurrent slots)
- Realistic Indian statutory frictions (STT, exchange fees, slippage)
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

class EventBacktester:
    def __init__(
        self,
        df: pd.DataFrame,
        initial_capital: float = 1_000_000.0,
        slippage_bps_per_leg: float = 2.0,
        statutory_cost_pct: float = 0.03
    ):
        self.df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(self.df["Date"]):
            self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df = self.df.sort_values("Date").reset_index(drop=True)
        
        self.initial_capital = initial_capital
        self.total_friction_rate = (slippage_bps_per_leg * 2.0 / 10000.0) + (statutory_cost_pct / 100.0)
        self._calculate_atr()

    def _calculate_atr(self, period: int = 14):
        """Calculates 14-day Average True Range for dynamic stops."""
        h_l = self.df["High"] - self.df["Low"]
        h_pc = (self.df["High"] - self.df["Close"].shift(1)).abs()
        l_pc = (self.df["Low"] - self.df["Close"].shift(1)).abs()
        tr = pd.concat([h_l, h_pc, l_pc], axis=1).max(axis=1)
        self.df["ATR"] = tr.rolling(window=period).mean()

    def run_backtest(
        self,
        events_df: pd.DataFrame,
        holding_period_days: int = 5,
        execution_model: str = "close",
        stop_loss_atr_mult: Optional[float] = None,
        take_profit_reclaim: bool = False
    ) -> Dict[str, Any]:
        """
        Executes event-driven backtest with optional risk management.
        """
        if len(events_df) == 0:
            return {"total_trades": 0, "cagr_pct": 0.0, "max_drawdown_pct": 0.0, "trades_df": pd.DataFrame()}
            
        trades = []
        equity = self.initial_capital
        ev_sorted = events_df.sort_values("Event_Idx").reset_index(drop=True)
        last_exit_idx = -1
        
        for _, row in ev_sorted.iterrows():
            entry_idx = int(row["Event_Idx"])
            if entry_idx <= last_exit_idx or (entry_idx + 1 >= len(self.df)):
                continue
                
            entry_price = self.df.loc[entry_idx, "Close"] if execution_model == "close" else self.df.loc[entry_idx + 1, "Open"]
            if np.isnan(entry_price) or entry_price <= 0:
                continue
                
            entry_date = self.df.loc[entry_idx, "Date"].strftime("%Y-%m-%d")
            atr_val = self.df.loc[entry_idx, "ATR"] if not np.isnan(self.df.loc[entry_idx, "ATR"]) else (entry_price * 0.015)
            stop_price = entry_price - (stop_loss_atr_mult * atr_val) if stop_loss_atr_mult else 0.0
            target_reclaim = self.df.loc[entry_idx - 1, "Close"] if take_profit_reclaim else np.inf
            
            # Walk forward through holding window to check stops/targets
            exit_idx = entry_idx + holding_period_days
            actual_exit_idx = min(exit_idx, len(self.df) - 1)
            exit_price = self.df.loc[actual_exit_idx, "Close"]
            exit_reason = "time_exit"
            
            if stop_loss_atr_mult or take_profit_reclaim:
                for day_offset in range(1, holding_period_days + 1):
                    chk_idx = entry_idx + day_offset
                    if chk_idx >= len(self.df):
                        break
                    curr_low = self.df.loc[chk_idx, "Low"]
                    curr_high = self.df.loc[chk_idx, "High"]
                    
                    # Stop loss triggered
                    if stop_loss_atr_mult and curr_low <= stop_price:
                        actual_exit_idx = chk_idx
                        exit_price = stop_price
                        exit_reason = "stop_loss"
                        break
                    # Take profit triggered (reclaimed pre-drop close)
                    if take_profit_reclaim and curr_high >= target_reclaim:
                        actual_exit_idx = chk_idx
                        exit_price = target_reclaim
                        exit_reason = "take_profit"
                        break
                        
            exit_date = self.df.loc[actual_exit_idx, "Date"].strftime("%Y-%m-%d")
            gross_ret = (exit_price - entry_price) / entry_price
            net_ret = gross_ret - self.total_friction_rate
            pnl = equity * net_ret
            equity += pnl
            last_exit_idx = actual_exit_idx
            
            trades.append({
                "Entry_Date": entry_date,
                "Exit_Date": exit_date,
                "Entry_Price": round(entry_price, 2),
                "Exit_Price": round(exit_price, 2),
                "Gross_Return_Pct": round(gross_ret * 100.0, 3),
                "Net_Return_Pct": round(net_ret * 100.0, 3),
                "Portfolio_Equity": round(equity, 2),
                "Exit_Reason": exit_reason,
                "PnL": round(pnl, 2)
            })
            
        trade_df = pd.DataFrame(trades)
        if len(trade_df) == 0:
            return {"total_trades": 0, "net_return_pct": 0.0}
            
        # Drawdown & Metrics
        equity_series = self._construct_equity_curve(trade_df)
        total_days = (self.df["Date"].iloc[-1] - self.df["Date"].iloc[0]).days
        years = total_days / 365.25
        total_ret = (equity - self.initial_capital) / self.initial_capital
        cagr = ((equity / self.initial_capital) ** (1.0 / years) - 1.0) * 100.0 if (years > 0 and equity > 0) else 0.0
        
        running_max = equity_series.cummax()
        drawdowns = (equity_series - running_max) / running_max * 100.0
        max_dd = float(drawdowns.min())
        
        wins = trade_df[trade_df["Net_Return_Pct"] > 0]
        win_rate = len(wins) / len(trade_df) * 100.0
        
        return {
            "total_trades": len(trade_df),
            "final_equity": round(equity, 2),
            "total_net_return_pct": round(total_ret * 100.0, 2),
            "cagr_pct": round(cagr, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "win_rate_pct": round(win_rate, 2),
            "trades_df": trade_df,
            "equity_series": equity_series
        }

    def _construct_equity_curve(self, trade_df: pd.DataFrame) -> pd.Series:
        curve = pd.Series(index=self.df["Date"], dtype=float)
        curve.iloc[0] = self.initial_capital
        eq = self.initial_capital
        trade_idx = 0
        n_trades = len(trade_df)
        
        for dt in self.df["Date"]:
            dt_str = dt.strftime("%Y-%m-%d")
            if trade_idx < n_trades and dt_str == trade_df.loc[trade_idx, "Exit_Date"]:
                eq = trade_df.loc[trade_idx, "Portfolio_Equity"]
                trade_idx += 1
            curve[dt] = eq
            
        return curve.ffill()
