import unittest
import pandas as pd
import numpy as np
from src.event_detector import EventDetector
from src.backtester import EventBacktester

class TestAdvancedUpgrades(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range("2023-01-01", periods=20, freq="B")
        closes = [100.0] * 20
        # Day 3 drops 3%
        closes[3] = 97.0
        # Day 4 bounces to 99.0
        closes[4] = 99.0
        
        opens = [100.0] * 20
        opens[3] = 100.0
        opens[4] = 97.5
        
        volumes = [1000] * 20
        volumes[3] = 3000 # volume surge
        
        self.df = pd.DataFrame({
            "Date": dates,
            "Open": opens,
            "High": [max(o, c) + 1.0 for o, c in zip(opens, closes)],
            "Low": [min(o, c) - 1.0 for o, c in zip(opens, closes)],
            "Close": closes,
            "Volume": volumes
        })
        self.detector = EventDetector(self.df)

    def test_volume_surge_and_recovery_matrix(self):
        events = self.detector.detect_events(threshold_pct=-2.0, require_volume_surge=True)
        self.assertEqual(len(events), 1)
        self.assertEqual(events.iloc[0]["Event_Idx"], 3)
        self.assertTrue(events.iloc[0]["Volume_Surge"])
        
        rec_matrix = self.detector.compute_recovery_matrix(events)
        self.assertIn("Prob_Rec_50_pct_1d", rec_matrix)
        self.assertGreaterEqual(rec_matrix["Prob_Rec_50_pct_1d"], 0.0)

    def test_stop_loss_and_take_profit(self):
        events = self.detector.detect_events(threshold_pct=-2.0)
        bt = EventBacktester(self.df)
        res = bt.run_backtest(events, holding_period_days=5, take_profit_reclaim=True)
        self.assertGreater(res["total_trades"], 0)
        trades = res["trades_df"]
        self.assertIn(trades.iloc[0]["Exit_Reason"], ["take_profit", "time_exit", "stop_loss"])

if __name__ == "__main__":
    unittest.main()
