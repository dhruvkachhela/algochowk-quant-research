import unittest
import pandas as pd
import numpy as np
from src.event_detector import EventDetector

class TestEventDetector(unittest.TestCase):
    def setUp(self):
        # Create a deterministic synthetic price series with 10 days
        # Day 3 drops by 3%, Day 4 drops by 2.5% (clustered drops)
        dates = pd.date_range("2023-01-01", periods=10, freq="B")
        closes = [100.0, 101.0, 102.0, 98.94, 96.46, 97.5, 99.0, 100.5, 101.0, 102.0]
        opens = [100.0, 101.0, 102.0, 101.5, 98.0, 97.0, 98.0, 99.5, 101.0, 101.5]
        
        self.df = pd.DataFrame({
            "Date": dates,
            "Open": opens,
            "High": [max(o, c) + 1.0 for o, c in zip(opens, closes)],
            "Low": [min(o, c) - 1.0 for o, c in zip(opens, closes)],
            "Close": closes,
            "Volume": [1000] * 10
        })
        self.detector = EventDetector(self.df)

    def test_detects_fixed_threshold(self):
        # Day 3: (98.94 - 102.0)/102.0 = -3.0%
        # Day 4: (96.46 - 98.94)/98.94 = -2.5%
        events = self.detector.detect_events(threshold_pct=-2.0, filter_independent=False)
        self.assertEqual(len(events), 2)
        self.assertAlmostEqual(events.iloc[0]["Event_Drop_Pct"], -3.0, places=1)

    def test_independent_filter_skips_cluster(self):
        # With independent filter (window=3), Day 4 should be skipped
        events = self.detector.detect_events(threshold_pct=-2.0, filter_independent=True, independent_window=3)
        self.assertEqual(len(events), 1)
        self.assertEqual(events.iloc[0]["Event_Idx"], 3)

    def test_no_lookahead_forward_returns(self):
        events = self.detector.detect_events(threshold_pct=-2.0, holding_periods=[1, 2])
        # Event 0 is at idx 3 (Day 3 close = 98.94)
        # 1-day forward exit is idx 4 (Day 4 close = 96.46) -> ret = (96.46 - 98.94)/98.94 = -2.5%
        # 2-day forward exit is idx 5 (Day 5 close = 97.50) -> ret = (97.50 - 98.94)/98.94 = -1.45%
        self.assertAlmostEqual(events.iloc[0]["Fwd_Ret_Close_1d"], -2.506, places=2)
        self.assertAlmostEqual(events.iloc[0]["Fwd_Ret_Close_2d"], -1.455, places=2)

if __name__ == "__main__":
    unittest.main()
