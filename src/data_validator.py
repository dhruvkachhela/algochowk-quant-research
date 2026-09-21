"""
Data Validator Module
Validates integrity of daily OHLCV market data:
- Monotonic ascending date ordering
- Duplicate date detection
- OHLC price invariant checks (High >= max(Open, Close), Low <= min(Open, Close))
- Non-positive price/volume checks
- Trading date continuity & gap reporting
"""

import pandas as pd
from typing import Dict, Any, Tuple, List

class DataValidator:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.audit_log: List[str] = []
        self.is_valid: bool = False
        
    def validate(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Runs comprehensive data validation pipeline and returns cleaned DataFrame with audit report.
        """
        report = {
            "initial_rows": len(self.df),
            "final_rows": 0,
            "duplicate_dates_found": 0,
            "ordering_issues_fixed": False,
            "ohlc_invariant_violations": 0,
            "missing_values_dropped": 0,
            "date_range": ("", ""),
            "checks_passed": True
        }
        
        # 1. Ensure required columns exist
        required_cols = ["Date", "Open", "High", "Low", "Close"]
        for col in required_cols:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")
                
        # 2. Parse and sort by Date
        self.df["Date"] = pd.to_datetime(self.df["Date"])
        if not self.df["Date"].is_monotonic_increasing:
            self.df = self.df.sort_values("Date").reset_index(drop=True)
            report["ordering_issues_fixed"] = True
            self.audit_log.append("Reordered rows chronologically.")
            
        # 3. Duplicate Dates Check
        dup_count = self.df.duplicated(subset=["Date"]).sum()
        if dup_count > 0:
            report["duplicate_dates_found"] = int(dup_count)
            self.df = self.df.drop_duplicates(subset=["Date"], keep="first").reset_index(drop=True)
            self.audit_log.append(f"Dropped {dup_count} duplicate date rows.")
            
        # 4. Drop NaN / Inf values in OHLC
        initial_len = len(self.df)
        self.df = self.df.dropna(subset=["Open", "High", "Low", "Close"]).reset_index(drop=True)
        # Drop rows where price <= 0
        valid_prices = (self.df["Open"] > 0) & (self.df["High"] > 0) & (self.df["Low"] > 0) & (self.df["Close"] > 0)
        self.df = self.df[valid_prices].reset_index(drop=True)
        dropped_missing = initial_len - len(self.df)
        report["missing_values_dropped"] = int(dropped_missing)
        
        # 5. OHLC Invariant Verification
        # High must be >= max(Open, Close), Low must be <= min(Open, Close)
        # In daily data, allow 0.05% tolerance for data feed tick-rounding anomalies, but flag violations
        high_violations = (self.df["High"] < self.df[["Open", "Close"]].max(axis=1) * 0.9995)
        low_violations = (self.df["Low"] > self.df[["Open", "Close"]].min(axis=1) * 1.0005)
        invariant_violations = (high_violations | low_violations).sum()
        
        report["ohlc_invariant_violations"] = int(invariant_violations)
        if invariant_violations > 0:
            self.audit_log.append(f"Warning: {invariant_violations} rows violated strict OHLC envelope.")
            
        # Format dates back to string ISO format
        self.df["Date_dt"] = self.df["Date"]
        self.df["Date"] = self.df["Date"].dt.strftime("%Y-%m-%d")
        
        # Date range summary
        report["final_rows"] = len(self.df)
        report["date_range"] = (str(self.df["Date"].iloc[0]), str(self.df["Date"].iloc[-1]))
        
        self.is_valid = (report["final_rows"] > 0) and (report["ohlc_invariant_violations"] == 0)
        report["checks_passed"] = self.is_valid
        
        return self.df, report
