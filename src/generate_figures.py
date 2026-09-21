"""
Chart and Visualizations Generator for Research Note and Jupyter Notebook
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
    plt.rcParams.update({'font.sans-serif': 'Arial', 'font.size': 11})
    
    raw_df = pd.read_csv(DATA_FILE)
    validator = DataValidator(raw_df)
    clean_df, _ = validator.validate()
    
    detector = EventDetector(clean_df)
    stat_engine = StatisticalEngine(seed=42)
    backtester = EventBacktester(clean_df)
    
    holding_periods = [1, 2, 3, 5, 10]
    baselines = detector.get_unconditional_baseline(holding_periods)
    events = detector.detect_events(threshold_pct=-2.0, holding_periods=holding_periods)
    
    # 1. Figure 1: Forward Return Comparison (Event vs Baseline across Horizons)
    fig, ax = plt.subplots(figsize=(10, 5))
    horizons = ["1d", "2d", "3d", "5d", "10d"]
    base_means = [baselines[h].mean() for h in holding_periods]
    close_means = [events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    open_means = [events[f"Fwd_Ret_Open_{h}d"].mean() for h in holding_periods]
    
    x = np.arange(len(horizons))
    width = 0.25
    
    ax.bar(x - width, base_means, width, label="Unconditional Baseline", color="#7f8c8d")
    ax.bar(x, close_means, width, label="Post-Drop (T Close Entry)", color="#2980b9")
    ax.bar(x + width, open_means, width, label="Post-Drop (T+1 Open Entry)", color="#e74c3c")
    
    ax.set_xlabel("Forward Holding Horizon")
    ax.set_ylabel("Mean Return (%)")
    ax.set_title("NIFTY 50 Forward Returns: Event vs Baseline (2007–2026)")
    ax.set_xticks(x)
    ax.set_xticklabels(horizons)
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig1_forward_returns_comparison.png"), dpi=300)
    plt.close()
    
    # 2. Figure 2: Bull vs Bear Regime Decomposition (200 SMA)
    bull_events = events[events["Regime_Bull"] == True]
    bear_events = events[events["Regime_Bull"] == False]
    
    fig, ax = plt.subplots(figsize=(9, 5))
    bull_means = [bull_events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    bear_means = [bear_events[f"Fwd_Ret_Close_{h}d"].mean() for h in holding_periods]
    
    ax.plot(horizons, bull_means, marker="o", linewidth=2.5, color="#27ae60", label="Bull Regime (Price > 200 SMA, N=54)")
    ax.plot(horizons, bear_means, marker="s", linewidth=2.5, color="#c0392b", label="Bear Regime (Price < 200 SMA, N=146)")
    ax.plot(horizons, base_means, linestyle="--", color="#7f8c8d", label="Unconditional Baseline")
    
    ax.set_xlabel("Holding Horizon")
    ax.set_ylabel("Mean Return (%)")
    ax.set_title("Regime Falsification: Bull Dip-Buying vs Bear Falling Knife")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig2_regime_decomposition.png"), dpi=300)
    plt.close()
    
    # 3. Figure 3: Equity Curve of Mean-Reversion Strategy vs Buy & Hold
    bt_res = backtester.run_backtest(events, holding_period_days=5, execution_model="close")
    eq_series = bt_res["equity_series"]
    
    # NIFTY Buy & Hold baseline normalized to initial capital
    nifty_bh = (clean_df["Close"] / clean_df["Close"].iloc[0]) * 1_000_000.0
    nifty_bh.index = pd.to_datetime(clean_df["Date"])
    
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(nifty_bh.index, nifty_bh / 1_000_000.0, label="NIFTY 50 Buy & Hold (Benchmark)", color="#34495e", alpha=0.7)
    ax.plot(eq_series.index, eq_series / 1_000_000.0, label="5-Day Mean Reversion Strategy (Net of Friction)", color="#e67e22", linewidth=2.0)
    
    ax.set_yscale("log")
    ax.set_xlabel("Year")
    ax.set_ylabel("Portfolio Value (Log Scale, Base = 1.0)")
    ax.set_title("Portfolio Equity Trajectory: Mean-Reversion vs Buy & Hold (2007–2026)")
    ax.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(DOCS_DIR, "fig3_backtest_equity_curve.png"), dpi=300)
    plt.close()
    
    print("[OK] Generated all 3 publication-grade figures in docs/ directory.")

if __name__ == "__main__":
    generate_visualizations()
