import unittest
import pandas as pd
import numpy as np
from src.backtester import EventBacktester

class TestBacktester(unittest.TestCase):
    def setUp(self):
        dates = pd.date_range("2023-01-01", periods=20, freq="B")
        closes = [100.0] * 20
        # Trade 1: Enter at idx 2, exit at idx 7 (5d holding). Closes at 105.0 (+5% gross)
        closes[2] = 100.0
        closes[7] = 105.0
        # Trade 2: Enter at idx 10, exit at idx 15 (5d holding). Closes at 95.0 (-5% gross)
        closes[10] = 100.0
        closes[15] = 95.0
        
        self.df = pd.DataFrame({
            "Date": dates,
            "Open": closes,
            "High": [c + 1.0 for c in closes],
            "Low": [c - 1.0 for c in closes],
            "Close": closes,
            "Volume": [1000] * 20
        })
        
        self.events_df = pd.DataFrame({
            "Event_Idx": [2, 10],
            "Event_Date": [dates[2].strftime("%Y-%m-%d"), dates[10].strftime("%Y-%m-%d")]
        })

    def test_backtest_execution_and_friction(self):
        # 0.04% slippage + 0.03% statutory = 0.07% total friction
        bt = EventBacktester(self.df, initial_capital=100000.0, slippage_bps_per_leg=2.0, statutory_cost_pct=0.03)
        res = bt.run_backtest(self.events_df, holding_period_days=5, execution_model="close")
        
        self.assertEqual(res["total_trades"], 2)
        trades = res["trades_df"]
        
        # Trade 1: Gross +5.0%, Net = 5.0 - 0.07 = 4.93%
        self.assertAlmostEqual(trades.loc[0, "Net_Return_Pct"], 4.93, places=2)
        # Trade 2: Gross -5.0%, Net = -5.0 - 0.07 = -5.07%
        self.assertAlmostEqual(trades.loc[1, "Net_Return_Pct"], -5.07, places=2)
        self.assertEqual(res["win_rate_pct"], 50.0)

if __name__ == "__main__":
    unittest.main()
