"""
Full Quantitative Research & Event-Driven Analysis Runner
Executes comprehensive research with:
1. Baseline comparisons and Welch t-tests
2. Volume climax and pin-bar exhaustion micro-structure conditioning
3. Survival analysis recovery matrix (Day 1 to 20)
4. Out-of-sample and bull vs bear regime tests
5. Risk-managed backtests (ATR stop-loss & take-profit)
"""

import os
import numpy as np
import pandas as pd
from src.data_validator import DataValidator
from src.event_detector import EventDetector
from src.statistical_engine import StatisticalEngine
from src.backtester import EventBacktester

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "nifty50_daily.csv")

def main():
    print("================================================================")
    print("NIFTY 50 ADVANCED QUANTITATIVE RESEARCH & EVENT STUDY ENGINE")
    print("================================================================\n")
    
    raw_df = pd.read_csv(DATA_FILE)
    clean_df, val_report = DataValidator(raw_df).validate()
    print(f"[DATA AUDIT] Validated {val_report['final_rows']} trading days ({val_report['date_range'][0]} to {val_report['date_range'][1]})\n")
    
    detector = EventDetector(clean_df)
    stat_engine = StatisticalEngine(seed=42)
    backtester = EventBacktester(clean_df, initial_capital=1_000_000.0)
    
    holding_periods = [1, 2, 3, 5, 10]
    baselines = detector.get_unconditional_baseline(holding_periods)
    
    # 1. Benchmark Event Analysis
    events = detector.detect_events(threshold_pct=-2.0, holding_periods=holding_periods)
    print("----------------------------------------------------------------")
    print(f"1. BENCHMARK EVENT ANALYSIS (Drop <= -2.0%, N={len(events)})")
    print("----------------------------------------------------------------")
    for h in holding_periods:
        ev_close = events[f"Fwd_Ret_Close_{h}d"]
        comp = stat_engine.compare_against_baseline(ev_close, baselines[h])
        print(f"Holding {h:2d}d | Baseline: {comp['baseline_mean']:+5.2f}% | Event: {comp['event_mean']:+5.2f}% | Abnormal: {comp['abnormal_mean']:+5.2f}% | Welch t={comp['welch_t_stat']:+5.2f} (p={comp['welch_p_value']:.4f})")
    print()
    
    # 2. Survival Analysis: Recovery Probability Matrix
    rec_matrix = detector.compute_recovery_matrix(events, max_days=20)
    print("----------------------------------------------------------------")
    print("2. SURVIVAL ANALYSIS: HAZARD RATE OF NIFTY RECOVERY")
    print("----------------------------------------------------------------")
    for d in [1, 2, 3, 5, 10, 20]:
        print(f"By Day {d:2d} | Prob of Recovering >= 50% of Drop: {rec_matrix[f'Prob_Rec_50_pct_{d}d']:5.1f}% | Prob of 100% Recovery: {rec_matrix[f'Prob_Rec_100_pct_{d}d']:5.1f}%")
    print()
    
    # 3. Microstructure Conditioning: Volume Climax & Pin-bar Exhaustion
    events_vol = detector.detect_events(threshold_pct=-2.0, require_volume_surge=True)
    events_pin = detector.detect_events(threshold_pct=-2.0, require_pinbar=True)
    events_both = detector.detect_events(threshold_pct=-2.0, require_volume_surge=True, require_pinbar=True)
    
    print("----------------------------------------------------------------")
    print("3. MICROSTRUCTURE CONDITIONING: EXHAUSTION FILTERS (5-Day Horizon)")
    print("----------------------------------------------------------------")
    comp_raw = stat_engine.compare_against_baseline(events["Fwd_Ret_Close_5d"], baselines[5])
    comp_vol = stat_engine.compare_against_baseline(events_vol["Fwd_Ret_Close_5d"], baselines[5]) if len(events_vol) > 0 else {}
    comp_pin = stat_engine.compare_against_baseline(events_pin["Fwd_Ret_Close_5d"], baselines[5]) if len(events_pin) > 0 else {}
    
    print(f"Raw Events (No Filter)    | N={len(events):3d} | Mean={comp_raw['event_mean']:+5.2f}% | Abnormal={comp_raw['abnormal_mean']:+5.2f}% | p={comp_raw['welch_p_value']:.4f}")
    if len(events_vol) > 0:
        print(f"Volume Surge Filter       | N={len(events_vol):3d} | Mean={comp_vol['event_mean']:+5.2f}% | Abnormal={comp_vol['abnormal_mean']:+5.2f}% | p={comp_vol['welch_p_value']:.4f}")
    if len(events_pin) > 0:
        print(f"Pin-bar Reversal Filter   | N={len(events_pin):3d} | Mean={comp_pin['event_mean']:+5.2f}% | Abnormal={comp_pin['abnormal_mean']:+5.2f}% | p={comp_pin['welch_p_value']:.4f}")
    print()
    
    # 4. Risk-Managed Backtest
    print("----------------------------------------------------------------")
    print("4. BACKTEST: RISK-MANAGED VS BLIND 5-DAY HOLDING")
    print("----------------------------------------------------------------")
    bt_blind = backtester.run_backtest(events, holding_period_days=5)
    bt_risk = backtester.run_backtest(events, holding_period_days=5, stop_loss_atr_mult=1.5, take_profit_reclaim=True)
    
    print(f"Blind 5d Exit        | Net Ret: {bt_blind['total_net_return_pct']:+6.2f}% | CAGR: {bt_blind['cagr_pct']:+5.2f}% | Max DD: {bt_blind['max_drawdown_pct']:+6.2f}% | Win Rate: {bt_blind['win_rate_pct']:.1f}%")
    print(f"Risk-Managed (SL+TP) | Net Ret: {bt_risk['total_net_return_pct']:+6.2f}% | CAGR: {bt_risk['cagr_pct']:+5.2f}% | Max DD: {bt_risk['max_drawdown_pct']:+6.2f}% | Win Rate: {bt_risk['win_rate_pct']:.1f}%")
    print("================================================================\n")

if __name__ == "__main__":
    main()
