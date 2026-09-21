"""
Figures Generator
Produces 4 publication-grade figures:
1. Fig 1: Forward Returns vs Baseline across Horizons
2. Fig 2: Regime Decomposition (Bull Price > 200 SMA vs Bear Price < 200 SMA)
3. Fig 3: Academic Cumulative Abnormal Return (CAR) Event Study Window [T-5 to T+10]
4. Fig 4: Empirical Recovery Probability Curve (Kaplan-Meier Style)
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from src.data_validator import DataValidator
from src.event_detector import EventDetector
from src.statistical_engine import StatisticalEngine
from src.backtester import EventBacktester

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nifty50_daily.csv")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def generate_visualizations():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 10})
    
    raw_df = pd.read_csv(DATA_FILE)
    clean_df, _ = DataValidator(raw_df).validate()
    
    detector = EventDetector(clean_df)
    holding_periods = [1, 2, 3, 5, 10]
    baselines = detector.get_unconditional_baseline(holding_periods)
    events = detector.detect_events(threshold_pct=-2.0, holding_periods=holding_periods)
    
    # 1. Figure 1: Forward Return Comparison
    fig, ax = plt.subplots(figsize=(9, 4.5))
    horizons = ["1d", "2d", "3d", "5d", "10d"]
    base_means = [baselines[h].mean() for h in holding_periods]
    close_means = [events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    open_means = [events[f"Fwd_Ret_Open_{h}d"].mean() for h in holding_periods]
    
    x = np.arange(len(horizons))
    width = 0.25
    ax.bar(x - width, base_means, width, label="Unconditional Baseline", color="#7f8c8d")
    ax.bar(x, close_means, width, label="Post-Drop (T Close Entry)", color="#2980b9")
    ax.bar(x + width, open_means, width, label="Post-Drop (T+1 Open Entry)", color="#e74c3c")
    ax.set_xlabel("Holding Horizon")
    ax.set_ylabel("Mean Return (%)")
    ax.set_title("NIFTY 50 Forward Returns: Event vs Baseline (2007–2026)")
    ax.set_xticks(x)
    ax.set_xticklabels(horizons)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig1_forward_returns_comparison.png"), dpi=300)
    plt.close()
    
    # 2. Figure 2: Bull vs Bear Regime Decomposition
    bull_events = events[events["Regime_Bull"] == True]
    bear_events = events[events["Regime_Bull"] == False]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bull_means = [bull_events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    bear_means = [bear_events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    ax.plot(horizons, bull_means, marker="o", linewidth=2.0, color="#27ae60", label="Bull Regime (Price > 200 SMA, N=54)")
    ax.plot(horizons, bear_means, marker="s", linewidth=2.0, color="#c0392b", label="Bear Regime (Price < 200 SMA, N=146)")
    ax.plot(horizons, base_means, linestyle="--", color="#7f8c8d", label="Unconditional Baseline")
    ax.set_xlabel("Holding Horizon")
    ax.set_ylabel("Mean Return (%)")
    ax.set_title("Regime Falsification: Bull Dip-Buying vs Bear Downside Momentum")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig2_regime_decomposition.png"), dpi=300)
    plt.close()
    
    # 3. Figure 3: Academic Event Study Trajectory Window [T-5 to T+10]
    traj_df = detector.get_event_study_trajectory(events["Event_Idx"].tolist(), pre_days=5, post_days=10)
    mean_traj = traj_df.mean()
    median_traj = traj_df.median()
    p25_traj = traj_df.quantile(0.25)
    p75_traj = traj_df.quantile(0.75)
    
    fig, ax = plt.subplots(figsize=(10, 4.8))
    days_axis = list(traj_df.columns)
    ax.plot(days_axis, mean_traj, color="#2c3e50", linewidth=2.2, label="Mean Path")
    ax.plot(days_axis, median_traj, color="#2980b9", linestyle="--", linewidth=1.8, label="Median Path")
    ax.fill_between(days_axis, p25_traj, p75_traj, color="#3498db", alpha=0.18, label="Interquartile Range (25th-75th %ile)")
    ax.axvline(x="T0", color="#e74c3c", linestyle=":", linewidth=2.0, label="Event Crash Day (T0)")
    ax.axhline(y=100.0, color="#bdc3c7", linestyle="--", linewidth=1.0)
    ax.set_xlabel("Event Window Relative Days")
    ax.set_ylabel("Normalized Price Index (T0 Close = 100.0)")
    ax.set_title("Academic Event Study: NIFTY 50 Trajectory Around -2% Crash Days")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig3_event_study_trajectory.png"), dpi=300)
    plt.close()
    
    # 4. Figure 4: Empirical Recovery Probability Curve
    rec_dict = detector.compute_recovery_matrix(events, max_days=20)
    days_k = [1, 2, 3, 5, 10, 20]
    prob_50 = [rec_dict[f"Prob_Rec_50_pct_{d}d"] for d in days_k]
    prob_100 = [rec_dict[f"Prob_Rec_100_pct_{d}d"] for d in days_k]
    
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(days_k, prob_50, marker="o", linewidth=2.0, color="#3498db", label="Prob of Recovering >= 50% of Drop")
    ax.plot(days_k, prob_100, marker="s", linewidth=2.0, color="#9b59b6", label="Prob of Recovering 100% of Drop")
    ax.set_xlabel("Days Elapsed After Crash (K)")
    ax.set_ylabel("Empirical Probability (%)")
    ax.set_title("Survival Analysis: Cumulative Probability of NIFTY Recovery by Day K")
    ax.set_xticks(days_k)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig4_recovery_probability_curve.png"), dpi=300)
    plt.close()
    
    print("[OK] All 4 publication-grade figures generated successfully in docs/.")

if __name__ == "__main__":
    generate_visualizations()
