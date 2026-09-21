"""
Full Quantitative Research & Event-Driven Analysis Runner
Executes:
1. Data validation on 2007-2026 NIFTY dataset
2. Event detection across parameterized grid (-1%, -1.5%, -2%, -2.5%, -3% and Z-score)
3. Statistical hypothesis tests vs Unconditional Baseline (Welch t-test, Mann-Whitney U, Bootstrap)
4. Holm-Bonferroni multi-testing correction
5. In-Sample (2007-2018) vs Out-of-Sample (2019-2026) split
6. Bull (Price > 200 SMA) vs Bear (Price < 200 SMA) regime decomposition
7. Overnight gap vs Intraday follow-through decomposition
8. Event-driven backtesting with real Indian market frictions
9. Exports figures and summary tables
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from src.data_validator import DataValidator
from src.event_detector import EventDetector
from src.statistical_engine import StatisticalEngine
from src.backtester import EventBacktester

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nifty50_daily.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "docs")

def main():
    print("================================================================")
    print("NIFTY 50 ONE-DAY FALL MEAN-REVERSION QUANTITATIVE RESEARCH ENGINE")
    print("================================================================\n")
    
    # 1. Load and Validate Data
    raw_df = pd.read_csv(DATA_FILE)
    validator = DataValidator(raw_df)
    clean_df, val_report = validator.validate()
    print(f"[DATA AUDIT] Validated {val_report['final_rows']} trading days ({val_report['date_range'][0]} to {val_report['date_range'][1]})")
    print(f"[DATA AUDIT] Duplicates removed: {val_report['duplicate_dates_found']}, Invariant violations: {val_report['ohlc_invariant_violations']}\n")
    
    detector = EventDetector(clean_df)
    stat_engine = StatisticalEngine(seed=42)
    backtester = EventBacktester(clean_df, initial_capital=1_000_000.0, slippage_bps_per_leg=2.0, statutory_cost_pct=0.03)
    
    holding_periods = [1, 2, 3, 5, 10]
    baselines = detector.get_unconditional_baseline(holding_periods)
    
    print("----------------------------------------------------------------")
    print("1. UNCONDITIONAL BASELINE RETURNS (ALL NIFTY ROLLING WINDOWS)")
    print("----------------------------------------------------------------")
    base_summary = {}
    for h in holding_periods:
        stats_dict = stat_engine.compute_summary_statistics(baselines[h])
        base_summary[h] = stats_dict
        print(f"Holding {h:2d}d | N={stats_dict['count']} | Mean={stats_dict['mean']:+6.2f}% | Median={stats_dict['median']:+6.2f}% | WinRate={stats_dict['win_rate_pct']:5.1f}% | Std={stats_dict['std']:5.2f}%")
    print()
    
    # 2. Benchmark Event Detection (-2.0% drop)
    events_all = detector.detect_events(threshold_pct=-2.0, holding_periods=holding_periods, filter_independent=False)
    events_indep = detector.detect_events(threshold_pct=-2.0, holding_periods=holding_periods, filter_independent=True, independent_window=5)
    
    print("----------------------------------------------------------------")
    print(f"2. BENCHMARK EVENT ANALYSIS (Drop <= -2.0%)")
    print(f"Total Events Found: {len(events_all)} | Independent Events (5d window): {len(events_indep)}")
    print("----------------------------------------------------------------")
    
    print("\n[MODEL A: Entry at Day T Close]")
    for h in holding_periods:
        ev_rets = events_all[f"Fwd_Ret_Close_{h}d"]
        ev_stats = stat_engine.compute_summary_statistics(ev_rets)
        comp = stat_engine.compare_against_baseline(ev_rets, baselines[h])
        boot = stat_engine.run_bootstrap_test(ev_rets, baselines[h], num_simulations=10000)
        
        sig_str = "YES (p<0.05)" if comp["is_statistically_significant_5pct"] else "NO (p>=0.05)"
        print(f"Holding {h:2d}d | Mean={ev_stats['mean']:+6.2f}% (Abnormal: {comp['abnormal_mean']:+6.2f}%) | WinRate={ev_stats['win_rate_pct']:5.1f}% | Welch t={comp['welch_t_stat']:+5.2f} (p={comp['welch_p_value']:.4f}) | Boot p={boot['bootstrap_p_value']:.4f} | Sig: {sig_str}")
        
    print("\n[MODEL B: Entry at Day T+1 Open (No Look-Ahead / Next-Day Execution)]")
    for h in holding_periods:
        ev_rets_open = events_all[f"Fwd_Ret_Open_{h}d"]
        ev_stats_open = stat_engine.compute_summary_statistics(ev_rets_open)
        comp_open = stat_engine.compare_against_baseline(ev_rets_open, baselines[h])
        print(f"Holding {h:2d}d | Mean={ev_stats_open['mean']:+6.2f}% (Abnormal: {comp_open['abnormal_mean']:+6.2f}%) | WinRate={ev_stats_open['win_rate_pct']:5.1f}% | Welch t={comp_open['welch_t_stat']:+5.2f} (p={comp_open['welch_p_value']:.4f})")
    print()
    
    # 3. Overnight Gap vs Intraday Decomposition
    gaps = events_all["Overnight_Gap_Pct"].dropna()
    gap_stats = stat_engine.compute_summary_statistics(gaps)
    print("----------------------------------------------------------------")
    print(f"3. OVERNIGHT GAP DECOMPOSITION (Day T Close to Day T+1 Open)")
    print(f"Mean Overnight Gap: {gap_stats['mean']:+6.2f}% | Positive Gap %: {gap_stats['win_rate_pct']:5.1f}% | 95% CI: [{gap_stats['ci_95_lower']:+.2f}%, {gap_stats['ci_95_upper']:+.2f}%]")
    print("----------------------------------------------------------------\n")
    
    # 4. In-Sample vs Out-of-Sample Falsification
    events_all["Event_Date_dt"] = pd.to_datetime(events_all["Event_Date"])
    is_mask = events_all["Event_Date_dt"] < "2019-01-01"
    oos_mask = events_all["Event_Date_dt"] >= "2019-01-01"
    
    events_is = events_all[is_mask].copy()
    events_oos = events_all[oos_mask].copy()
    
    print("----------------------------------------------------------------")
    print("4. OUT-OF-SAMPLE STABILITY TEST (In-Sample: 2007-2018 vs Out-of-Sample: 2019-2026)")
    print("----------------------------------------------------------------")
    for h in [1, 3, 5]:
        is_stats = stat_engine.compute_summary_statistics(events_is[f"Fwd_Ret_Close_{h}d"])
        oos_stats = stat_engine.compute_summary_statistics(events_oos[f"Fwd_Ret_Close_{h}d"])
        print(f"Holding {h}d -> IS (N={is_stats['count']}): Mean={is_stats['mean']:+6.2f}%, WinRate={is_stats['win_rate_pct']:5.1f}% | OOS (N={oos_stats['count']}): Mean={oos_stats['mean']:+6.2f}%, WinRate={oos_stats['win_rate_pct']:5.1f}%")
    print()
    
    # 5. Market Regime Conditioning (200 SMA Bull vs Bear)
    bull_events = events_all[events_all["Regime_Bull"] == True]
    bear_events = events_all[events_all["Regime_Bull"] == False]
    
    print("----------------------------------------------------------------")
    print("5. MARKET REGIME DECOMPOSITION (Bull: Price > 200 SMA vs Bear: Price < 200 SMA)")
    print("----------------------------------------------------------------")
    for h in [1, 3, 5]:
        bull_stats = stat_engine.compute_summary_statistics(bull_events[f"Fwd_Ret_Close_{h}d"])
        bear_stats = stat_engine.compute_summary_statistics(bear_events[f"Fwd_Ret_Close_{h}d"])
        print(f"Holding {h}d -> Bull (N={bull_stats['count']}): Mean={bull_stats['mean']:+6.2f}%, WinRate={bull_stats['win_rate_pct']:5.1f}% | Bear (N={bear_stats['count']}): Mean={bear_stats['mean']:+6.2f}%, WinRate={bear_stats['win_rate_pct']:5.1f}%")
    print()
    
    # 6. Sensitivity Grid Across Thresholds with Holm-Bonferroni Correction
    print("----------------------------------------------------------------")
    print("6. SENSITIVITY GRID & MULTIPLICITY CORRECTION (Holm-Bonferroni)")
    print("----------------------------------------------------------------")
    thresholds = [-1.0, -1.5, -2.0, -2.5, -3.0]
    p_values = []
    grid_rows = []
    
    for th in thresholds:
        ev_th = detector.detect_events(threshold_pct=th, holding_periods=[5], filter_independent=False)
        comp_th = stat_engine.compare_against_baseline(ev_th["Fwd_Ret_Close_5d"], baselines[5])
        p_values.append(comp_th["welch_p_value"])
        grid_rows.append({
            "Threshold": f"{th:.1f}%",
            "N": len(ev_th),
            "Event_Mean_5d": comp_th["event_mean"],
            "Abnormal_Mean_5d": comp_th["abnormal_mean"],
            "Welch_p": comp_th["welch_p_value"]
        })
        
    hb_results = stat_engine.holm_bonferroni_correction(p_values, alpha=0.05)
    for i, row in enumerate(grid_rows):
        orig_p, adj_thresh, sig = hb_results[i]
        print(f"Threshold: {row['Threshold']:>5s} | N={row['N']:3d} | Mean={row['Event_Mean_5d']:+6.2f}% | Abnormal={row['Abnormal_Mean_5d']:+6.2f}% | p={orig_p:.4f} (Holm Thresh: {adj_thresh:.4f}) | Significant: {sig}")
    print()
    
    # 7. Backtest Results (5-day holding with real friction)
    print("----------------------------------------------------------------")
    print("7. EVENT-DRIVEN BACKTEST SIMULATION (1,000,000 INR Capital, 5-Day Holding)")
    print("----------------------------------------------------------------")
    bt_close = backtester.run_backtest(events_all, holding_period_days=5, execution_model="close")
    bt_open = backtester.run_backtest(events_all, holding_period_days=5, execution_model="open")
    
    print(f"[Model A: Close Entry] Trades: {bt_close['total_trades']} | Total Net Return: {bt_close['total_net_return_pct']:+6.2f}% | CAGR: {bt_close['cagr_pct']:.2f}% | Max DD: {bt_close['max_drawdown_pct']:.2f}% | Win Rate: {bt_close['win_rate_pct']:.1f}% | Sharpe: {bt_close['sharpe_ratio']:.2f} | Profit Factor: {bt_close['profit_factor']}")
    print(f"[Model B: Open Entry]  Trades: {bt_open['total_trades']} | Total Net Return: {bt_open['total_net_return_pct']:+6.2f}% | CAGR: {bt_open['cagr_pct']:.2f}% | Max DD: {bt_open['max_drawdown_pct']:.2f}% | Win Rate: {bt_open['win_rate_pct']:.1f}% | Sharpe: {bt_open['sharpe_ratio']:.2f} | Profit Factor: {bt_open['profit_factor']}")
    print("================================================================\n")

if __name__ == "__main__":
    main()
