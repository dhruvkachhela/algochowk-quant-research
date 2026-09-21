"""
Event Detector Module
Identifies one-day drop events and computes forward holding period returns.
Supports:
- Parameterized percentage thresholds (-1.0%, -1.5%, -2.0%, -2.5%, -3.0%)
- Volatility-standardized drop thresholds (z-score <= -2.0)
- Dual execution timing models (Day T Close vs Day T+1 Open)
- Event clustering filters (All Events vs Independent Non-Overlapping Events)
- Forward holding horizon returns for H in [1, 2, 3, 5, 10] days
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
        """Calculates single-day close-to-close returns and 20-day rolling volatility."""
        self.df["Return_1d"] = self.df["Close"].pct_change()
        self.df["Return_1d_pct"] = self.df["Return_1d"] * 100.0
        
        # 20-day rolling mean & standard deviation for volatility-standardized drops
        self.df["Rolling_Mean_20"] = self.df["Return_1d"].rolling(window=20).mean()
        self.df["Rolling_Std_20"] = self.df["Return_1d"].rolling(window=20).std()
        self.df["Z_Score_20"] = (self.df["Return_1d"] - self.df["Rolling_Mean_20"]) / self.df["Rolling_Std_20"]
        
        # 200-day Simple Moving Average for market regime classification
        self.df["SMA_200"] = self.df["Close"].rolling(window=200).mean()
        self.df["Regime_Bull"] = self.df["Close"] > self.df["SMA_200"]
        
    def detect_events(
        self,
        threshold_pct: float = -2.0,
        use_volatility_zscore: bool = False,
        z_threshold: float = -2.0,
        holding_periods: List[int] = [1, 2, 3, 5, 10],
        filter_independent: bool = False,
        independent_window: int = 5
    ) -> pd.DataFrame:
        """
        Scans for one-day drop events and computes forward returns.
        
        Parameters:
        - threshold_pct: Drop threshold in percent (e.g. -2.0 for -2% fall)
        - use_volatility_zscore: If True, uses z-score drop instead of fixed percent
        - z_threshold: Volatility z-score threshold (e.g. -2.0)
        - holding_periods: List of holding periods in trading days to evaluate
        - filter_independent: If True, drops events that occur within `independent_window` of a prior event
        - independent_window: Cooldown window in trading days for independent filtering
        """
        events = []
        n_rows = len(self.df)
        max_h = max(holding_periods)
        
        last_event_idx = -9999
        
        for i in range(1, n_rows):
            ret_pct = self.df.loc[i, "Return_1d_pct"]
            z_score = self.df.loc[i, "Z_Score_20"]
            
            # Check event condition
            if use_volatility_zscore:
                is_event = (not np.isnan(z_score)) and (z_score <= z_threshold)
            else:
                is_event = ret_pct <= threshold_pct
                
            if not is_event:
                continue
                
            # Check independence constraint if enabled
            if filter_independent:
                if (i - last_event_idx) < independent_window:
                    continue
                last_event_idx = i
            else:
                last_event_idx = i
                
            event_date = self.df.loc[i, "Date"]
            event_close = self.df.loc[i, "Close"]
            event_ret = ret_pct
            regime_bull = bool(self.df.loc[i, "Regime_Bull"])
            
            # Next day open (for Model B execution)
            next_open = self.df.loc[i + 1, "Open"] if (i + 1 < n_rows) else np.nan
            
            event_record = {
                "Event_Idx": i,
                "Event_Date": event_date.strftime("%Y-%m-%d"),
                "Event_Drop_Pct": event_ret,
                "Event_Close": event_close,
                "Next_Open": next_open,
                "Regime_Bull": regime_bull,
                "Overnight_Gap_Pct": ((next_open - event_close) / event_close * 100.0) if not np.isnan(next_open) else np.nan
            }
            
            # Forward returns for each holding horizon
            for h in holding_periods:
                target_idx = i + h
                if target_idx < n_rows:
                    exit_close = self.df.loc[target_idx, "Close"]
                    exit_date = self.df.loc[target_idx, "Date"].strftime("%Y-%m-%d")
                    
                    # Model A: Entry at Event Close (T Close)
                    fwd_ret_close = (exit_close - event_close) / event_close * 100.0
                    
                    # Model B: Entry at Next Open (T+1 Open)
                    if not np.isnan(next_open):
                        fwd_ret_open = (exit_close - next_open) / next_open * 100.0
                    else:
                        fwd_ret_open = np.nan
                        
                    event_record[f"Exit_Date_{h}d"] = exit_date
                    event_record[f"Fwd_Ret_Close_{h}d"] = fwd_ret_close
                    event_record[f"Fwd_Ret_Open_{h}d"] = fwd_ret_open
                else:
                    event_record[f"Exit_Date_{h}d"] = None
                    event_record[f"Fwd_Ret_Close_{h}d"] = np.nan
                    event_record[f"Fwd_Ret_Open_{h}d"] = np.nan
                    
            events.append(event_record)
            
        return pd.DataFrame(events)
        
    def get_unconditional_baseline(self, holding_periods: List[int] = [1, 2, 3, 5, 10]) -> Dict[int, pd.Series]:
        """
        Calculates the unconditional rolling baseline forward returns for all trading days.
        """
        baselines = {}
        for h in holding_periods:
            fwd_ret = (self.df["Close"].shift(-h) - self.df["Close"]) / self.df["Close"] * 100.0
            baselines[h] = fwd_ret.dropna()
        return baselines
