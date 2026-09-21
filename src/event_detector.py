"""
Event Detector Module
Identifies one-day drop events and computes forward holding period returns.
Includes institutional microstructure filters:
- Volume Climax / Capitulation: Volume > 1.5 * 20d rolling mean
- Lower Shadow / Pin-bar: (Close - Low) / (High - Low) >= 0.35 (buyer exhaustion off lows)
- Multi-horizon forward returns (H in 1, 2, 3, 5, 10 days)
- Event trajectory extraction (T-5 to T+10 window)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple

class EventDetector:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if not pd.api.types.is_datetime64_any_dtype(self.df["Date"]):
            self.df["Date"] = pd.to_datetime(self.df["Date"])
        self.df = self.df.sort_values("Date").reset_index(drop=True)
        self._calculate_base_returns()
        
    def _calculate_base_returns(self):
        """Calculates single-day close-to-close returns, volume dynamics, and regime flags."""
        self.df["Return_1d"] = self.df["Close"].pct_change()
        self.df["Return_1d_pct"] = self.df["Return_1d"] * 100.0
        
        # 20-day rolling return metrics
        self.df["Rolling_Mean_20"] = self.df["Return_1d"].rolling(window=20).mean()
        self.df["Rolling_Std_20"] = self.df["Return_1d"].rolling(window=20).std()
        self.df["Z_Score_20"] = (self.df["Return_1d"] - self.df["Rolling_Mean_20"]) / self.df["Rolling_Std_20"]
        
        # 200-day Simple Moving Average for market regime classification
        self.df["SMA_200"] = self.df["Close"].rolling(window=200).mean()
        self.df["Regime_Bull"] = self.df["Close"] > self.df["SMA_200"]
        
        # Volume Climax & Candlestick Tail metrics (Microstructure signals)
        self.df["Volume_Mean_20"] = self.df["Volume"].rolling(window=20, min_periods=1).mean()
        self.df["Volume_Surge"] = self.df["Volume"] > (1.5 * self.df["Volume_Mean_20"])
        
        # Lower wick ratio: (Close - Low) / (High - Low)
        hl_spread = self.df["High"] - self.df["Low"]
        self.df["Lower_Wick_Ratio"] = np.where(hl_spread > 0, (self.df["Close"] - self.df["Low"]) / hl_spread, 0.0)
        self.df["Is_Pinbar"] = self.df["Lower_Wick_Ratio"] >= 0.35
        
    def detect_events(
        self,
        threshold_pct: float = -2.0,
        holding_periods: List[int] = [1, 2, 3, 5, 10],
        filter_independent: bool = False,
        independent_window: int = 5,
        require_volume_surge: bool = False,
        require_pinbar: bool = False
    ) -> pd.DataFrame:
        """
        Scans for drop events with optional microstructure filters.
        """
        events = []
        n_rows = len(self.df)
        last_event_idx = -9999
        
        for i in range(1, n_rows):
            ret_pct = self.df.loc[i, "Return_1d_pct"]
            if ret_pct > threshold_pct:
                continue
                
            # Optional microstructure filters
            if require_volume_surge and not self.df.loc[i, "Volume_Surge"]:
                continue
            if require_pinbar and not self.df.loc[i, "Is_Pinbar"]:
                continue
                
            # Independent filtering
            if filter_independent and (i - last_event_idx) < independent_window:
                continue
            last_event_idx = i
            
            event_date = self.df.loc[i, "Date"]
            event_close = self.df.loc[i, "Close"]
            regime_bull = bool(self.df.loc[i, "Regime_Bull"])
            next_open = self.df.loc[i + 1, "Open"] if (i + 1 < n_rows) else np.nan
            
            rec = {
                "Event_Idx": i,
                "Event_Date": event_date.strftime("%Y-%m-%d"),
                "Event_Drop_Pct": ret_pct,
                "Event_Close": event_close,
                "Next_Open": next_open,
                "Regime_Bull": regime_bull,
                "Volume_Surge": bool(self.df.loc[i, "Volume_Surge"]),
                "Is_Pinbar": bool(self.df.loc[i, "Is_Pinbar"]),
                "Overnight_Gap_Pct": ((next_open - event_close) / event_close * 100.0) if not np.isnan(next_open) else np.nan
            }
            
            # Forward returns for each holding horizon
            for h in holding_periods:
                target_idx = i + h
                if target_idx < n_rows:
                    exit_close = self.df.loc[target_idx, "Close"]
                    rec[f"Exit_Date_{h}d"] = self.df.loc[target_idx, "Date"].strftime("%Y-%m-%d")
                    rec[f"Fwd_Ret_Close_{h}d"] = (exit_close - event_close) / event_close * 100.0
                    rec[f"Fwd_Ret_Open_{h}d"] = ((exit_close - next_open) / next_open * 100.0) if not np.isnan(next_open) else np.nan
                else:
                    rec[f"Exit_Date_{h}d"] = None
                    rec[f"Fwd_Ret_Close_{h}d"] = np.nan
                    rec[f"Fwd_Ret_Open_{h}d"] = np.nan
                    
            events.append(rec)
            
        return pd.DataFrame(events)

    def get_event_study_trajectory(self, event_indices: List[int], pre_days: int = 5, post_days: int = 10) -> pd.DataFrame:
        """
        Extracts normalized price paths [-pre_days, +post_days] relative to Day T Close (indexed at 100.0).
        """
        n_rows = len(self.df)
        trajectories = []
        
        for idx in event_indices:
            if idx - pre_days >= 0 and idx + post_days < n_rows:
                event_close = self.df.loc[idx, "Close"]
                slice_closes = self.df.loc[idx - pre_days : idx + post_days, "Close"].to_numpy()
                norm_path = (slice_closes / event_close) * 100.0
                trajectories.append(norm_path)
                
        cols = [f"T{'+' if offset >= 0 else ''}{offset}" for offset in range(-pre_days, post_days + 1)]
        return pd.DataFrame(trajectories, columns=cols)
        
    def compute_recovery_matrix(self, events_df: pd.DataFrame, max_days: int = 20) -> Dict[str, float]:
        """
        Calculates empirical probability of recovering 50% and 100% of the drop within K days.
        """
        n_rows = len(self.df)
        rec_50_count = {d: 0 for d in [1, 2, 3, 5, 10, 20]}
        rec_100_count = {d: 0 for d in [1, 2, 3, 5, 10, 20]}
        total = len(events_df)
        if total == 0:
            return {}
            
        for _, row in events_df.iterrows():
            idx = int(row["Event_Idx"])
            drop = abs(row["Event_Drop_Pct"])
            entry_price = row["Event_Close"]
            target_50 = entry_price * (1.0 + (drop * 0.5) / 100.0)
            target_100 = entry_price * (1.0 + drop / 100.0)
            
            for k in [1, 2, 3, 5, 10, 20]:
                horizon_idx = min(idx + k, n_rows - 1)
                max_high = self.df.loc[idx + 1 : horizon_idx, "High"].max() if (idx + 1 <= horizon_idx) else entry_price
                if max_high >= target_50:
                    rec_50_count[k] += 1
                if max_high >= target_100:
                    rec_100_count[k] += 1
                    
        return {
            f"Prob_Rec_50_pct_{k}d": round((rec_50_count[k] / total) * 100.0, 1) for k in [1, 2, 3, 5, 10, 20]
        } | {
            f"Prob_Rec_100_pct_{k}d": round((rec_100_count[k] / total) * 100.0, 1) for k in [1, 2, 3, 5, 10, 20]
        }

    def get_unconditional_baseline(self, holding_periods: List[int] = [1, 2, 3, 5, 10]) -> Dict[int, pd.Series]:
        """Calculates unconditional rolling baseline forward returns."""
        baselines = {}
        for h in holding_periods:
            fwd_ret = (self.df["Close"].shift(-h) - self.df["Close"]) / self.df["Close"] * 100.0
            baselines[h] = fwd_ret.dropna()
        return baselines
