import unittest
import pandas as pd
import numpy as np
from src.data_validator import DataValidator

class TestDataValidator(unittest.TestCase):
    def setUp(self):
        # Create a sample valid DataFrame
        dates = pd.date_range("2023-01-01", periods=10, freq="B")
        self.valid_df = pd.DataFrame({
            "Date": dates,
            "Open": [100.0 + i for i in range(10)],
            "High": [105.0 + i for i in range(10)],
            "Low": [95.0 + i for i in range(10)],
            "Close": [102.0 + i for i in range(10)],
            "Volume": [1000 * (i + 1) for i in range(10)]
        })

    def test_valid_data_passes(self):
        validator = DataValidator(self.valid_df)
        df, report = validator.validate()
        self.assertTrue(report["checks_passed"])
        self.assertEqual(report["final_rows"], 10)
        self.assertEqual(report["ohlc_invariant_violations"], 0)

    def test_reordering_and_duplicates(self):
        # Shuffle order and add duplicate
        shuffled = self.valid_df.iloc[[3, 1, 0, 2, 2, 4]].copy()
        validator = DataValidator(shuffled)
        df, report = validator.validate()
        self.assertTrue(report["ordering_issues_fixed"])
        self.assertEqual(report["duplicate_dates_found"], 1)
        self.assertEqual(report["final_rows"], 5)

    def test_invalid_ohlc_flagged(self):
        # High < Low violation
        invalid_df = self.valid_df.copy()
        invalid_df.loc[2, "High"] = 90.0  # lower than Low (97.0)
        validator = DataValidator(invalid_df)
        df, report = validator.validate()
        self.assertFalse(report["checks_passed"])
        self.assertGreater(report["ohlc_invariant_violations"], 0)

if __name__ == "__main__":
    unittest.main()
