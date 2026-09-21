"""
Event-Driven Backtester Module
Simulates realistic execution of mean-reversion strategy on NIFTY index/ETF:
- Entry at Day T Close (Model A) or Day T+1 Open (Model B)
- Exit at Day T+H Close
- Realistic transaction friction (STT, exchange turnover fees, GST, and bid-ask slippage)
- Performance metrics: CAGR, Max Drawdown, Win Rate, Sharpe Ratio, Profit Factor, Trade Log
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class EventBacktester:
    def __init__(
        self,
        df: pd.DataFrame,
        initial_capital: float = 1_000_000.0,
        slippage_bps_per_leg: float = 2.0,   # 2 bps per leg = 0.02%
        statutory_cost_pct: float = 0.03     # 0.03% round-trip (STT, NSE fees, GST)
    ):
        self.df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(self.df["Date"]):
            self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df = self.df.sort_values("Date").reset_index(drop=True)
        
        self.initial_capital = initial_capital
        self.slippage_rate = (slippage_bps_per_leg / 10000.0) * 2.0  # round-trip slippage
        self.total_friction_rate = self.slippage_rate + (statutory_cost_pct / 100.0)
        
    def run_backtest(
        self,
        events_df: pd.DataFrame,
        holding_period_days: int = 5,
        execution_model: str = "close" # 'close' (Model A) or 'open' (Model B)
    ) -> Dict[str, Any]:
        """
        Executes an event-driven backtest simulation.
        """
        if len(events_df) == 0:
            return {
                "total_trades": 0, "cagr_pct": 0.0, "sharpe_ratio": 0.0,
                "max_drawdown_pct": 0.0, "win_rate_pct": 0.0, "equity_curve": pd.DataFrame()
            }
            
        trades = []
        equity = self.initial_capital
        
        # Sort events chronologically
        ev_sorted = events_df.sort_values("Event_Idx").reset_index(drop=True)
        
        # Simulate sequential non-overlapping trade executions
        last_exit_idx = -1
        
        for _, row in ev_sorted.iterrows():
            entry_idx = int(row["Event_Idx"])
            exit_idx = entry_idx + holding_period_days
            
            # Avoid overlapping trades in single capital allocation
            if entry_idx <= last_exit_idx:
                continue
            if exit_idx >= len(self.df):
                continue
                
            entry_date = self.df.loc[entry_idx, "Date"].strftime("%Y-%m-%d")
            exit_date = self.df.loc[exit_idx, "Date"].strftime("%Y-%m-%d")
            
            if execution_model.lower() == "open":
                entry_price = self.df.loc[entry_idx + 1, "Open"] if (entry_idx + 1 < len(self.df)) else np.nan
            else:
                entry_price = self.df.loc[entry_idx, "Close"]
                
            exit_price = self.df.loc[exit_idx, "Close"]
            
            if np.isnan(entry_price) or entry_price <= 0:
                continue
                
            # Gross Return
            gross_ret = (exit_price - entry_price) / entry_price
            # Net Return after total friction (slippage + STT/taxes)
            net_ret = gross_ret - self.total_friction_rate
            
            pnl = equity * net_ret
            equity += pnl
            last_exit_idx = exit_idx
            
            trades.append({
                "Entry_Date": entry_date,
                "Exit_Date": exit_date,
                "Execution_Model": execution_model,
                "Entry_Price": entry_price,
                "Exit_Price": exit_price,
                "Gross_Return_Pct": round(gross_ret * 100.0, 3),
                "Net_Return_Pct": round(net_ret * 100.0, 3),
                "Portfolio_Equity": round(equity, 2),
                "PnL": round(pnl, 2)
            })
            
        trade_df = pd.DataFrame(trades)
        if len(trade_df) == 0:
            return {"total_trades": 0, "net_return_pct": 0.0}
            
        # Daily Equity Curve reconstruction
        equity_series = self._construct_equity_curve(trade_df)
        
        # Performance & Risk Metrics
        total_days = (self.df["Date"].iloc[-1] - self.df["Date"].iloc[0]).days
        years = total_days / 365.25
        total_ret = (equity - self.initial_capital) / self.initial_capital
        cagr = ((equity / self.initial_capital) ** (1.0 / years) - 1.0) * 100.0 if (years > 0 and equity > 0) else 0.0
        
        # Drawdown calculation
        running_max = equity_series.cummax()
        drawdowns = (equity_series - running_max) / running_max * 100.0
        max_dd = float(drawdowns.min())
        
        # Trade statistics
        wins = trade_df[trade_df["Net_Return_Pct"] > 0]
        losses = trade_df[trade_df["Net_Return_Pct"] < 0]
        win_rate = len(wins) / len(trade_df) * 100.0
        
        gross_profit = wins["PnL"].sum() if len(wins) > 0 else 0.0
        gross_loss = abs(losses["PnL"].sum()) if len(losses) > 0 else 1.0
        profit_factor = round(gross_profit / gross_loss, 2) if gross_loss > 0 else np.nan
        
        # Annualized Sharpe ratio on daily trade-holding returns
        trade_rets = trade_df["Net_Return_Pct"] / 100.0
        sharpe = float((trade_rets.mean() / trade_rets.std()) * np.sqrt(252 / holding_period_days)) if trade_rets.std() > 0 else 0.0
        
        return {
            "total_trades": len(trade_df),
            "final_equity": round(equity, 2),
            "total_net_return_pct": round(total_ret * 100.0, 2),
            "cagr_pct": round(cagr, 2),
            "max_drawdown_pct": round(max_dd, 2),
            "win_rate_pct": round(win_rate, 2),
            "profit_factor": profit_factor,
            "sharpe_ratio": round(sharpe, 2),
            "trades_df": trade_df,
            "equity_series": equity_series
        }
        
    def _construct_equity_curve(self, trade_df: pd.DataFrame) -> pd.Series:
        """Constructs mark-to-market portfolio value trajectory across calendar time."""
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
