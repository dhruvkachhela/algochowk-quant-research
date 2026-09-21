import unittest
import pandas as pd
import numpy as np
from src.statistical_engine import StatisticalEngine

class TestStatisticalEngine(unittest.TestCase):
    def setUp(self):
        self.engine = StatisticalEngine(seed=42)
        # Create deterministic synthetic normal series
        np.random.seed(42)
        self.baseline = pd.Series(np.random.normal(loc=0.3, scale=1.0, size=500))
        self.events_positive = pd.Series(np.random.normal(loc=1.2, scale=1.0, size=50))
        self.events_noise = pd.Series(np.random.normal(loc=0.32, scale=1.0, size=50))

    def test_summary_statistics(self):
        stats_dict = self.engine.compute_summary_statistics(self.events_positive)
        self.assertEqual(stats_dict["count"], 50)
        self.assertAlmostEqual(stats_dict["mean"], 1.2, delta=0.3)
        self.assertTrue(stats_dict["ci_95_lower"] < stats_dict["mean"] < stats_dict["ci_95_upper"])

    def test_welch_t_test_detects_significance(self):
        res_sig = self.engine.compare_against_baseline(self.events_positive, self.baseline)
        self.assertTrue(res_sig["is_statistically_significant_5pct"])
        self.assertLess(res_sig["welch_p_value"], 0.01)

        res_noise = self.engine.compare_against_baseline(self.events_noise, self.baseline)
        self.assertFalse(res_noise["is_statistically_significant_5pct"])
        self.assertGreater(res_noise["welch_p_value"], 0.05)

    def test_holm_bonferroni_correction(self):
        p_vals = [0.001, 0.02, 0.045, 0.30]
        corrected = self.engine.holm_bonferroni_correction(p_vals, alpha=0.05)
        # 0.001 <= 0.05/4 (0.0125) -> True
        self.assertTrue(corrected[0][2])
        # 0.30 is not significant
        self.assertFalse(corrected[3][2])

if __name__ == "__main__":
    unittest.main()
