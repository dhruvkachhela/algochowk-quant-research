"""
Statistical Engine Module
Performs rigorous hypothesis testing, baseline comparisons, and bootstrap simulations:
- Summary metrics: Count, Mean, Median, Win Rate, Volatility, Skewness, Kurtosis
- Two-sample Welch's t-test (Event vs Unconditional Baseline)
- Non-parametric Mann-Whitney U test
- 10,000-sample Circular Block Bootstrap for autocorrelation-preserving empirical p-values & CIs
- Holm-Bonferroni multi-testing correction across parameter grids
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Any, List, Tuple

class StatisticalEngine:
    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed)
        
    def compute_summary_statistics(self, series: pd.Series) -> Dict[str, float]:
        """Calculates core distribution statistics for a return series."""
        clean = series.dropna().to_numpy()
        n = len(clean)
        if n == 0:
            return {
                "count": 0, "mean": np.nan, "median": np.nan,
                "win_rate_pct": np.nan, "std": np.nan,
                "skewness": np.nan, "kurtosis": np.nan,
                "ci_95_lower": np.nan, "ci_95_upper": np.nan
            }
            
        mean_val = float(np.mean(clean))
        std_val = float(np.std(clean, ddof=1)) if n > 1 else 0.0
        se = std_val / np.sqrt(n) if n > 1 else 0.0
        
        # 95% Student-t confidence interval
        t_crit = stats.t.ppf(0.975, df=n-1) if n > 1 else 1.96
        ci_lower = mean_val - t_crit * se
        ci_upper = mean_val + t_crit * se
        
        return {
            "count": int(n),
            "mean": round(mean_val, 4),
            "median": round(float(np.median(clean)), 4),
            "win_rate_pct": round(float(np.sum(clean > 0) / n * 100.0), 2),
            "std": round(std_val, 4),
            "skewness": round(float(stats.skew(clean)), 4) if n > 2 else 0.0,
            "kurtosis": round(float(stats.kurtosis(clean)), 4) if n > 3 else 0.0,
            "ci_95_lower": round(ci_lower, 4),
            "ci_95_upper": round(ci_upper, 4)
        }
        
    def compare_against_baseline(
        self,
        event_returns: pd.Series,
        baseline_returns: pd.Series
    ) -> Dict[str, Any]:
        """
        Runs two-sample Welch t-test and Mann-Whitney U test between event returns and baseline.
        """
        ev = event_returns.dropna().to_numpy()
        base = baseline_returns.dropna().to_numpy()
        
        n_ev = len(ev)
        n_base = len(base)
        
        if n_ev == 0 or n_base == 0:
            return {
                "abnormal_mean": np.nan,
                "welch_t_stat": np.nan,
                "welch_p_value": np.nan,
                "mann_whitney_u": np.nan,
                "mann_whitney_p_value": np.nan,
                "is_statistically_significant_5pct": False
            }
            
        mean_ev = np.mean(ev)
        mean_base = np.mean(base)
        abnormal_mean = mean_ev - mean_base
        
        # Welch's t-test (unequal variances)
        t_stat, t_pval = stats.ttest_ind(ev, base, equal_var=False)
        
        # Mann-Whitney U test (non-parametric rank-sum test)
        u_stat, u_pval = stats.mannwhitneyu(ev, base, alternative="two-sided")
        
        return {
            "event_mean": round(float(mean_ev), 4),
            "baseline_mean": round(float(mean_base), 4),
            "abnormal_mean": round(float(abnormal_mean), 4),
            "welch_t_stat": round(float(t_stat), 4),
            "welch_p_value": round(float(t_pval), 6),
            "mann_whitney_u": round(float(u_stat), 2),
            "mann_whitney_p_value": round(float(u_pval), 6),
            "is_statistically_significant_5pct": bool(t_pval < 0.05)
        }
        
    def run_bootstrap_test(
        self,
        event_returns: pd.Series,
        baseline_returns: pd.Series,
        num_simulations: int = 10000,
        block_size: int = 5
    ) -> Dict[str, Any]:
        """
        Performs a circular block bootstrap to test the null hypothesis that post-event returns
        are no different from baseline market returns, preserving autocorrelation.
        """
        ev = event_returns.dropna().to_numpy()
        base = baseline_returns.dropna().to_numpy()
        n_ev = len(ev)
        n_base = len(base)
        
        if n_ev == 0 or n_base == 0:
            return {"bootstrap_p_value": np.nan, "bootstrap_ci_95": (np.nan, np.nan)}
            
        observed_mean_diff = np.mean(ev) - np.mean(base)
        
        # Circular block bootstrap from baseline
        simulated_diffs = np.zeros(num_simulations)
        num_blocks = int(np.ceil(n_ev / block_size))
        
        for sim in range(num_simulations):
            # Draw random block starting points
            start_indices = self.rng.integers(0, n_base, size=num_blocks)
            sampled_indices = []
            for idx in start_indices:
                block = [(idx + k) % n_base for k in range(block_size)]
                sampled_indices.extend(block)
            sampled_indices = sampled_indices[:n_ev]
            
            sample_returns = base[sampled_indices]
            simulated_diffs[sim] = np.mean(sample_returns) - np.mean(base)
            
        # Empirical two-sided p-value: fraction of simulated differences >= observed absolute diff
        emp_pval = np.mean(np.abs(simulated_diffs) >= np.abs(observed_mean_diff))
        
        # 95% Bootstrap Confidence Interval of the observed mean
        event_boot_means = np.zeros(num_simulations)
        for sim in range(num_simulations):
            resampled_ev = self.rng.choice(ev, size=n_ev, replace=True)
            event_boot_means[sim] = np.mean(resampled_ev)
            
        ci_lower = np.percentile(event_boot_means, 2.5)
        ci_upper = np.percentile(event_boot_means, 97.5)
        
        return {
            "observed_mean_diff": round(float(observed_mean_diff), 4),
            "bootstrap_p_value": round(float(emp_pval), 6),
            "bootstrap_ci_95": (round(float(ci_lower), 4), round(float(ci_upper), 4)),
            "is_significant_bootstrap_5pct": bool(emp_pval < 0.05)
        }
        
    @staticmethod
    def holm_bonferroni_correction(p_values: List[float], alpha: float = 0.05) -> List[Tuple[float, float, bool]]:
        """
        Applies Holm-Bonferroni step-down correction for multiple hypothesis tests.
        Returns list of (original_pval, adjusted_threshold, is_significant).
        """
        m = len(p_values)
        indexed = sorted(enumerate(p_values), key=lambda x: x[1])
        results = [None] * m
        
        for rank, (orig_idx, pval) in enumerate(indexed):
            thresh = alpha / (m - rank)
            sig = pval <= thresh
            results[orig_idx] = (round(pval, 6), round(thresh, 6), sig)
            
        return results
