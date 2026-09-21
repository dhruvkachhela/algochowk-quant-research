# NIFTY 50 Post-Crash Mean-Reversion Quantitative Research
### AlgoChowk — Quant Engineer Intern Assignment

Investigating the hypothesis:  
**"After a significant one-day fall in NIFTY, the market tends to recover over the next few trading days."**

---

## 1. Executive Summary & Key Empirical Findings

This repository provides an institutional-grade quantitative event study and backtest of the post-crash mean-reversion anomaly on the **NIFTY 50 Index (`^NSEI`)** across 19 years (September 2007 to September 2026, 4,664 trading days).

### Core Findings:
1. **Statistical Insignificance**: Following a single-day drop of 2% or more (N=200), average 5-day forward return is **+0.32%** compared to the unconditional baseline of **+0.21%** (Abnormal Return = +0.10%, Welch t-test p-value = **0.8031**, 10,000-sample Block Bootstrap p-value = **0.7863**). The bounce is statistically indistinguishable from random market drift.
2. **Survival Analysis & Recovery Hazard Rate**: By Day 1, the probability of recovering 100% of the drop is only **14.5%**. By Day 5, the probability of full recovery is only **49.0%**. Over 51% of all crash days remain unrecovered after an entire trading week.
3. **Execution Timing & Overnight Gap Decay**: The marginal edge (+0.15% average overnight gap) is inaccessible to intraday traders. When executed realistically at Day T+1 Open, the 5-day return drops to **+0.16%** (Abnormal Return = -0.06%, Welch t-stat = -0.15, p = 0.8836).
4. **Regime Asymmetry**: In secular bull regimes (Price > 200 SMA), 3-day recovery averages **+0.65%** (59.3% win rate). In bear regimes (Price < 200 SMA, where 73% of large drops occur), recovery collapses to **+0.14%** (52.7% win rate) due to downside momentum and volatility clustering.
5. **Microstructure Conditioning**: Candlestick pin-bars with strong lower shadows (buyers absorbing selling pressure before close) produce a 5-day bounce of **+1.57%** (N=25).
6. **Risk Management vs Blind Holding**: Blind 5-day holding yields a negative return of **-7.16%** with a **-46.18%** max drawdown. Adding a 1.5x ATR trailing stop-loss and early take-profit upon reclaiming pre-drop levels turns the strategy net positive to **+0.82%**.

---

## 2. Minimalist Repository Structure

```
algochowk-quant-research/
├── data/
│   ├── fetch_data.py               # Automated Yahoo Finance chart API downloader
│   └── nifty50_daily.csv           # 2007-2026 verified NIFTY daily OHLCV dataset
├── src/
│   ├── __init__.py
│   ├── data_validator.py           # Validates OHLC envelopes, chronological order, duplicates
│   ├── event_detector.py           # Parameterized event scanner, microstructure filters, recovery matrix
│   ├── statistical_engine.py       # Welch t-test, Mann-Whitney U, Block Bootstrap, Holm-Bonferroni
│   ├── backtester.py               # Event backtester with ATR stop-loss, take-profit & friction
│   ├── run_research.py             # Full research pipeline and statistical summary generator
│   └── generate_figures.py         # Publication chart generator (4 high-res figures)
├── tests/
│   ├── __init__.py
│   └── test_all.py                 # Unified, single test suite covering all modules
├── notebooks/
│   └── nifty_event_study.ipynb     # Interactive research notebook with narrative and plots
├── docs/
│   ├── research_note.md            # Max 2-page publication-grade Research Note
│   ├── fig1_forward_returns_comparison.png
│   ├── fig2_regime_decomposition.png
│   ├── fig3_event_study_trajectory.png
│   └── fig4_recovery_probability_curve.png
└── README.md                       # Master repository documentation
```

---

## 3. Quick Start & Reproduction

### Run Unified Test Suite
```powershell
python -m unittest tests.test_all
```

### Run Full Research Analysis
```powershell
python -m src.run_research
```

### Generate Figures
```powershell
python -m src.generate_figures
```

---

## 4. Key Results Summary Tables

### Benchmark Event Analysis (Drop <= -2.0%, N = 200)
| Horizon | Baseline Mean (%) | Model A (Close) Mean (%) | Abnormal Mean (%) | Welch t-stat | Welch p-val | Bootstrap p-val | Significant (p<0.05) | Model B (Open) Mean (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1d** | +0.04% | +0.11% | +0.06% | +0.35 | 0.7291 | 0.4804 | **False** | -0.04% |
| **2d** | +0.09% | +0.09% | +0.00% | +0.01 | 0.9946 | 0.9925 | **False** | -0.06% |
| **3d** | +0.13% | +0.28% | +0.15% | +0.47 | 0.6405 | 0.5426 | **False** | +0.12% |
| **5d** | +0.21% | +0.32% | +0.10% | +0.25 | 0.8031 | 0.7863 | **False** | +0.16% |
| **10d** | +0.42% | +0.60% | +0.18% | +0.34 | 0.7364 | 0.7546 | **False** | +0.44% |

### Survival Analysis: Hazard Rate of Recovery by Day K
| Elapsed Trading Days (K) | Cumulative Probability of 50% Recovery | Cumulative Probability of 100% Recovery | Failure Rate (Unrecovered) |
|:---:|:---:|:---:|:---:|
| **Day 1** | 43.5% | 14.5% | 85.5% |
| **Day 2** | 59.0% | 26.0% | 74.0% |
| **Day 3** | 65.5% | 39.0% | 61.0% |
| **Day 5** | 72.0% | 49.0% | 51.0% |
| **Day 10** | 81.5% | 65.5% | 34.5% |
| **Day 20** | 85.5% | 74.5% | 25.5% |

### Microstructure Conditioning (5-Day Horizon)
| Strategy Filter | Sample Size (N) | 5d Mean Return | Abnormal Return | Welch p-value | Significant |
|---|:---:|:---:|:---:|:---:|:---:|
| **Raw Events (No Filter)** | 200 | +0.32% | +0.10% | 0.8031 | No |
| **Volume Surge Filter** | 15 | -1.34% | -1.56% | 0.4331 | No |
| **Pin-bar Reversal Filter** | 25 | **+1.57%** | **+1.36%** | 0.3612 | No |

### Backtest Strategy Performance (1,000,000 INR Capital, Friction = 0.07%)
| Strategy Variant | Total Net Return | CAGR | Max Drawdown | Win Rate | Profit Factor |
|---|:---:|:---:|:---:|:---:|:---:|
| **Model A: Close Entry (Blind 5d Exit)** | -7.16% | -0.39% | -46.18% | 50.8% | 0.96 |
| **Model B: Open Entry (Blind 5d Exit)** | -16.71% | -0.96% | -45.75% | 49.2% | 0.90 |
| **Risk-Managed (1.5x ATR Stop + Take-Profit)** | **+0.82%** | **+0.04%** | -52.38% | **54.4%** | **1.02** |

---

## 5. Live Research Engine Terminal Output

When you run `python -m src.run_research`, the engine produces the following output:

```text
================================================================
NIFTY 50 ADVANCED QUANTITATIVE RESEARCH & EVENT STUDY ENGINE
================================================================

[DATA AUDIT] Validated 4664 trading days (2007-09-17 to 2026-09-21)

----------------------------------------------------------------
1. BENCHMARK EVENT ANALYSIS (Drop <= -2.0%, N=200)
----------------------------------------------------------------
Holding  1d | Baseline: +0.04% | Event: +0.11% | Abnormal: +0.06% | Welch t=+0.35 (p=0.7291)
Holding  2d | Baseline: +0.09% | Event: +0.09% | Abnormal: +0.00% | Welch t=+0.01 (p=0.9946)
Holding  3d | Baseline: +0.13% | Event: +0.28% | Abnormal: +0.15% | Welch t=+0.47 (p=0.6405)
Holding  5d | Baseline: +0.21% | Event: +0.32% | Abnormal: +0.10% | Welch t=+0.25 (p=0.8031)
Holding 10d | Baseline: +0.42% | Event: +0.60% | Abnormal: +0.18% | Welch t=+0.34 (p=0.7364)

----------------------------------------------------------------
2. SURVIVAL ANALYSIS: HAZARD RATE OF NIFTY RECOVERY
----------------------------------------------------------------
By Day  1 | Prob of Recovering >= 50% of Drop:  43.5% | Prob of 100% Recovery:  14.5%
By Day  2 | Prob of Recovering >= 50% of Drop:  59.0% | Prob of 100% Recovery:  26.0%
By Day  3 | Prob of Recovering >= 50% of Drop:  65.5% | Prob of 100% Recovery:  39.0%
By Day  5 | Prob of Recovering >= 50% of Drop:  72.0% | Prob of 100% Recovery:  49.0%
By Day 10 | Prob of Recovering >= 50% of Drop:  81.5% | Prob of 100% Recovery:  65.5%
By Day 20 | Prob of Recovering >= 50% of Drop:  85.5% | Prob of 100% Recovery:  74.5%

----------------------------------------------------------------
3. MICROSTRUCTURE CONDITIONING: EXHAUSTION FILTERS (5-Day Horizon)
----------------------------------------------------------------
Raw Events (No Filter)    | N=200 | Mean=+0.32% | Abnormal=+0.10% | p=0.8031
Volume Surge Filter       | N= 15 | Mean=-1.34% | Abnormal=-1.56% | p=0.4331
Pin-bar Reversal Filter   | N= 25 | Mean=+1.57% | Abnormal=+1.36% | p=0.3612

----------------------------------------------------------------
4. BACKTEST: RISK-MANAGED VS BLIND 5-DAY HOLDING
----------------------------------------------------------------
Blind 5d Exit        | Net Ret:  -7.16% | CAGR: -0.39% | Max DD: -46.18% | Win Rate: 50.8%
Risk-Managed (SL+TP) | Net Ret:  +0.82% | CAGR: +0.04% | Max DD: -52.38% | Win Rate: 54.4%
================================================================
```

---

## 6. Visualizations

| Forward Returns vs Baseline | Regime Falsification (200 SMA) |
|:---:|:---:|
| ![Forward Returns](docs/fig1_forward_returns_comparison.png) | ![Regime Decomposition](docs/fig2_regime_decomposition.png) |

| Academic Event Trajectory [T-5 to T+10] | Survival Recovery Probability Curve |
|:---:|:---:|
| ![Event Trajectory](docs/fig3_event_study_trajectory.png) | ![Recovery Curve](docs/fig4_recovery_probability_curve.png) |

---

## 7. Official Research Note
* **[Research Note (2 Pages)](docs/research_note.md)**
