# NIFTY 50 Post-Crash Mean-Reversion Quantitative Research
### AlgoChowk — Quant Engineer Intern Assignment

Investigating the hypothesis:  
**"After a significant one-day fall in NIFTY, the market tends to recover over the next few trading days."**

---

## 1. Project Overview & Findings

This repository provides an institutional-grade quantitative event study and backtest of the post-crash mean-reversion anomaly on the **NIFTY 50 Index (`^NSEI`)** across 19 years (September 2007 to September 2026, 4,664 trading days).

### Key Research Findings:
1. **Statistical Insignificance**: Following a single-day drop of 2% or more (N=200), average 5-day forward return is **+0.32%** compared to the unconditional baseline of **+0.21%** (Abnormal Return = +0.10%, Welch t-test p-value = **0.8031**, 10,000-sample Block Bootstrap p-value = **0.7863**). The bounce is statistically indistinguishable from random market drift.
2. **Execution Timing & Overnight Gap**: The marginal edge (+0.15% average overnight gap) is inaccessible to intraday traders. When executed realistically at Day T+1 Open, the 5-day return drops to **+0.16%** (Abnormal Return = -0.06%, Welch t-stat = -0.15, p = 0.8836).
3. **Severe Regime Asymmetry**: In secular bull regimes (Price > 200 SMA), 3-day recovery averages **+0.65%** (59.3% win rate). In bear regimes (Price < 200 SMA, where 73% of large drops occur), recovery collapses to **+0.14%** (52.7% win rate) due to persistent downside momentum and volatility clustering.
4. **Economic Non-Viability**: After applying realistic Indian statutory costs (STT, NSE turnover fees, GST) and 4 bps round-trip slippage (0.07% total friction), a systematic 5-day mean-reversion strategy yields a **CAGR of -0.39%** with a **maximum drawdown of -46.18%**.

**Conclusion**: We **firmly reject the hypothesis** that an unconditioned single-day drop in NIFTY generates an actionable trading edge.

---

## 2. Repository Structure

```
algochowk-quant-research/
├── data/
│   ├── fetch_data.py               # Automated Yahoo Finance chart API downloader
│   └── nifty50_daily.csv           # 2007-2026 verified NIFTY daily OHLCV dataset
├── src/
│   ├── __init__.py
│   ├── data_validator.py           # Data validation, OHLC sanity, gap and duplicate checks
│   ├── event_detector.py           # Parameterized event scanner & forward return calculator
│   ├── statistical_engine.py       # Welch t-test, Mann-Whitney U, Block Bootstrap, Holm-Bonferroni
│   ├── backtester.py               # Event-driven backtest with real Indian market frictions
│   ├── run_research.py             # Full research pipeline and statistical summary generator
│   └── generate_figures.py         # Publication chart generator
├── tests/
│   ├── test_data_validator.py      # Unit tests for data validation
│   ├── test_event_detector.py      # Unit tests for event detection & zero look-ahead bias
│   ├── test_statistical_engine.py  # Unit tests for statistical hypothesis tests
│   └── test_backtester.py          # Unit tests for backtest mechanics & friction deductions
├── notebooks/
│   └── nifty_event_study.ipynb     # Interactive research notebook with full narrative and plots
├── docs/
│   ├── research_note.md            # Max 2-page publication-grade Research Note
│   ├── ai_usage_note.md            # Required 1-page AI Usage Note
│   ├── video_presentation.md       # 2-3 minute presentation script with slide guide
│   ├── fig1_forward_returns_comparison.png
│   ├── fig2_regime_decomposition.png
│   └── fig3_backtest_equity_curve.png
└── README.md                       # This document
```

---

## 3. Quick Start & Reproduction

### Prerequisites
* Python 3.10+
* Required packages: `pandas`, `numpy`, `scipy`, `statsmodels`, `matplotlib`, `seaborn`

### Step 1: Run Unit Tests
To verify all calculations and data integrity assertions:
```powershell
python -m unittest discover -s tests -v
```

### Step 2: Run the Quantitative Research Pipeline
To compute baseline comparisons, hypothesis tests, regime decomposition, and backtest results:
```powershell
python -m src.run_research
```

### Step 3: Generate Figures
To produce high-resolution figures in the `docs/` directory:
```powershell
python -m src.generate_figures
```

---

## 4. Key Results Summary Tables

### Benchmark Event Analysis (Drop <= -2.0%, N = 200)
| Horizon (Days) | Baseline Mean (%) | Model A (Close) Mean (%) | Abnormal Mean (%) | Welch t-stat | Welch p-value | Bootstrap p-val | Significant (alpha=0.05) | Model B (Open) Mean (%) |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **1d** | +0.04% | +0.11% | +0.06% | +0.35 | 0.7291 | 0.4804 | **False** | -0.04% |
| **2d** | +0.09% | +0.09% | +0.00% | +0.01 | 0.9946 | 0.9925 | **False** | -0.06% |
| **3d** | +0.13% | +0.28% | +0.15% | +0.47 | 0.6405 | 0.5426 | **False** | +0.12% |
| **5d** | +0.21% | +0.32% | +0.10% | +0.25 | 0.8031 | 0.7863 | **False** | +0.16% |
| **10d** | +0.42% | +0.60% | +0.18% | +0.34 | 0.7364 | 0.7546 | **False** | +0.44% |

### Multiplicity & Sensitivity Grid (5-Day Horizon with Holm-Bonferroni Correction)
| Threshold | Total Events (N) | Event Mean 5d (%) | Abnormal Mean (%) | Raw Welch p-value | Holm Adjusted Threshold | Statistically Significant |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **-1.0%** | 648 | +0.41% | +0.20% | 0.2396 | 0.0100 | **False** |
| **-1.5%** | 352 | +0.38% | +0.17% | 0.5222 | 0.0167 | **False** |
| **-2.0%** | 200 | +0.32% | +0.10% | 0.8031 | 0.0500 | **False** |
| **-2.5%** | 117 | +0.71% | +0.50% | 0.3813 | 0.0125 | **False** |
| **-3.0%** | 79 | +0.61% | +0.39% | 0.6072 | 0.0250 | **False** |

---

## 5. Submission Documents
* **[Research Note (2 Pages)](docs/research_note.md)**
* **[AI Usage Note (1 Page)](docs/ai_usage_note.md)**
* **[Video Presentation Script (2-3 Minutes)](docs/video_presentation.md)**
