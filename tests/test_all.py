"""
Unified Test Suite
Consolidates all unit tests for data validation, event detection,
statistical inference, backtesting, and risk management into a single file.
"""

import unittest
import pandas as pd
import numpy as np

from src.data_validator import DataValidator
from src.event_detector import EventDetector
from src.statistical_engine import StatisticalEngine
from src.backtester import EventBacktester

class TestQuantitativePipeline(unittest.TestCase):
    def setUp(self):
        # 1. Synthetic dataset for validator & detector
        dates = pd.date_range("2023-01-01", periods=20, freq="B")
        closes = [100.0] * 20
        closes[3] = 97.0   # Day 3 drops 3.0%
        closes[4] = 99.0   # Day 4 bounces to 99.0
        
        opens = [100.0] * 20
        opens[3] = 100.0
        opens[4] = 97.5
        
        volumes = [1000] * 20
        volumes[3] = 3000  # Volume surge on drop day
        
        self.sample_df = pd.DataFrame({
            "Date": dates,
            "Open": opens,
            "High": [max(o, c) + 1.0 for o, c in zip(opens, closes)],
            "Low": [min(o, c) - 1.0 for o, c in zip(opens, closes)],
            "Close": closes,
            "Volume": volumes
        })
        
        self.validator = DataValidator(self.sample_df)
        self.detector = EventDetector(self.sample_df)
        self.stat_engine = StatisticalEngine(seed=42)
        self.backtester = EventBacktester(self.sample_df, initial_capital=100_000.0)

    # --- Data Validator Tests ---
    def test_data_validation_integrity(self):
        clean_df, report = self.validator.validate()
        self.assertTrue(report["checks_passed"])
        self.assertEqual(report["final_rows"], 20)
        self.assertEqual(report["ohlc_invariant_violations"], 0)

    def test_invalid_ohlc_rejection(self):
        corrupt_df = self.sample_df.copy()
        corrupt_df.loc[2, "High"] = 80.0  # High lower than Low
        _, report = DataValidator(corrupt_df).validate()
        self.assertFalse(report["checks_passed"])
        self.assertGreater(report["ohlc_invariant_violations"], 0)

    # --- Event Detector Tests ---
    def test_event_detection_and_no_lookahead(self):
        events = self.detector.detect_events(threshold_pct=-2.0, holding_periods=[1, 2])
        self.assertEqual(len(events), 1)
        self.assertEqual(events.iloc[0]["Event_Idx"], 3)
        self.assertAlmostEqual(events.iloc[0]["Event_Drop_Pct"], -3.0, places=1)
        # Check forward returns
        self.assertAlmostEqual(events.iloc[0]["Fwd_Ret_Close_1d"], (99.0 - 97.0) / 97.0 * 100.0, places=2)

    def test_microstructure_and_recovery_matrix(self):
        events = self.detector.detect_events(threshold_pct=-2.0, require_volume_surge=True)
        self.assertEqual(len(events), 1)
        self.assertTrue(events.iloc[0]["Volume_Surge"])
        
        rec = self.detector.compute_recovery_matrix(events)
        self.assertIn("Prob_Rec_50_pct_1d", rec)
        self.assertGreaterEqual(rec["Prob_Rec_50_pct_1d"], 0.0)

    # --- Statistical Engine Tests ---
    def test_welch_t_test_and_bootstrap(self):
        base = pd.Series(np.random.normal(loc=0.3, scale=1.0, size=200))
        ev_sig = pd.Series(np.random.normal(loc=1.5, scale=1.0, size=50))
        
        comp = self.stat_engine.compare_against_baseline(ev_sig, base)
        self.assertTrue(comp["is_statistically_significant_5pct"])
        self.assertLess(comp["welch_p_value"], 0.01)
        
        p_vals = [0.001, 0.04, 0.20]
        corrected = self.stat_engine.holm_bonferroni_correction(p_vals)
        self.assertTrue(corrected[0][2])
        self.assertFalse(corrected[2][2])

    # --- Backtester & Risk Management Tests ---
    def test_backtest_execution_and_stops(self):
        events = self.detector.detect_events(threshold_pct=-2.0)
        res = self.backtester.run_backtest(events, holding_period_days=5, take_profit_reclaim=True)
        self.assertGreater(res["total_trades"], 0)
        trade = res["trades_df"].iloc[0]
        self.assertIn(trade["Exit_Reason"], ["take_profit", "time_exit", "stop_loss"])
        self.assertLess(trade["Net_Return_Pct"], trade["Gross_Return_Pct"]) # friction deducted

if __name__ == "__main__":
    unittest.main()
