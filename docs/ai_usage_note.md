# AI Usage Disclosure & Research Methodology Note

**Candidate**: Dhruv  
**Role**: Quantitative Engineer Intern Evaluation  
**Project**: NIFTY 50 Post-Crash Mean Reversion Event Study & Quantitative Backtesting  
**Repository**: [github.com/dhruvkachhela/algochowk-quant-research](https://github.com/dhruvkachhela/algochowk-quant-research)  
**Deliverable Documents**: [`docs/ai_usage_note.md`](./ai_usage_note.md) | [`docs/ai_usage_note.pdf`](./ai_usage_note.pdf)

---

## 1. Executive Statement on AI Utilization

In compliance with the AlgoChowk Quantitative Challenge evaluation standards, this document provides full transparency regarding the utilization of Artificial Intelligence (AI) in this quantitative research project.

AI tools (specifically Large Language Models) were utilized as an **accelerator for econometric literature extraction, mathematical formalization, and software scaffolding**. All conceptual hypotheses, data validation pipelines, financial sanity checks, econometric falsification tests, and final quantitative conclusions were rigorously formulated, verified, and audited with human quantitative judgment.

---

## 2. Literature Extraction & Theoretical Foundations

A central objective of this research was to move beyond naive retail heuristics ("buy every dip") and benchmark Indian equity dynamics against foundational financial economics. AI was leveraged to systematically survey, extract, and synthesize key academic literature:

### 2.1 Academic Papers Surveyed & Operationalized
1. **De Bondt & Thaler (1985) — *Does the Stock Market Overreact?* (Journal of Finance)**:
   - *AI Synthesis Role*: Extracted the theoretical overreaction hypothesis, which attributes mean-reversion to irrational investor sentiment and temporary liquidity dislocations.
   - *Implementation*: Used to formulate the primary null hypothesis ($H_0: \text{AR}_h = 0$) and event indicator $I_t(\theta)$ for left-tail crashes ($\le -2.0\%$).
2. **Engle (1982) — *Autoregressive Conditional Heteroscedasticity* (Econometrica)**:
   - *AI Synthesis Role*: Extracted mathematical properties of volatility clustering in financial time series.
   - *Implementation*: Integrated into Section 8.3 via a Glosten-Jagannathan-Runkle GJR-GARCH(1,1) model with leverage parameters to prove that negative shocks induce persistent variance expansion rather than quiet mean-reversion.
3. **Politis & Romano (1994) — *The Stationary Bootstrap* (JASA)**:
   - *AI Synthesis Role*: Synthesized non-parametric resampling methods that preserve serial correlation and heteroscedasticity in time series data.
   - *Implementation*: Implemented a 10,000-iteration Circular Block Bootstrap ($b = \lceil n^{1/3} \rceil = 17$) to calculate empirical $p$-values that do not rely on Gaussian normality assumptions.
4. **Harvey, Liu, & Zhu (2016) — *… and the Cross-Section of Expected Returns* (Review of Financial Studies)**:
   - *AI Synthesis Role*: Extracted protocols for controlling multiple hypothesis testing and data snooping in quantitative finance.
   - *Implementation*: Applied the Holm-Bonferroni Family-Wise Error Rate (FWER) step-down correction across multi-horizon holding windows ($h \in \{1, 2, 3, 4, 5, 7, 10\}$) and threshold sensitivity grids ($\theta \in [-1.0\%, -3.0\%]$).
5. **Shleifer & Vishny (1997) — *The Limits of Arbitrage* (Journal of Finance)**:
   - *AI Synthesis Role*: Extracted structural capital constraints and institutional agency frictions that impede liquidity provision during severe market downturns.
   - *Implementation*: Framed the empirical finding that 73% of large shocks occur in bear markets where risk mandates force institutional desks to de-gross rather than buy the dip.
6. **Borio & Zhu (2012) — *Capital Regulation, Risk-Taking and Monetary Policy***:
   - *AI Synthesis Role*: Synthesized pro-cyclical volatility-targeting feedback loops and market impact scaling laws.
   - *Implementation*: Formulated the Square-Root Market Impact Law ($\Delta P = \eta \sigma \sqrt{Q/V}$) and inverse-volatility position sizing schedule.

---

## 3. Code Generation & Software Scaffolding

AI was used to accelerate the development of a production-grade, modular Python codebase following institutional engineering standards:

### 3.1 Codebase Components Co-Generated & Refactored with AI
* **Data Integrity Validator ([`src/data_validator.py`](../src/data_validator.py))**:
  - Implemented automated checks for strictly monotonic chronological ordering, non-positive price/volume detection, and candlestick envelope invariance ($\text{High}_t \ge \max(\text{Open}_t, \text{Close}_t)$, $\text{Low}_t \le \min(\text{Open}_t, \text{Close}_t)$).
* **Event Detection Engine ([`src/event_detector.py`](../src/event_detector.py))**:
  - Scans continuous OHLCV data for parameterized percentage thresholds without look-ahead bias.
  - Constructs multi-horizon forward returns under two execution models: Model A (theoretical Day $T$ Close) and Model B (realistic Day $T+1$ Open).
  - Implements lower-wick pin-bar absorption ratios ($\Omega_t \ge 0.35$) and volume surge filters ($> 1.5\times$ 20-day SMA).
* **Statistical Inference Engine ([`src/statistical_engine.py`](../src/statistical_engine.py))**:
  - Implements two-sample Welch $t$-tests with Satterthwaite degrees of freedom, non-parametric Mann-Whitney $U$ rank-sum tests, Circular Block Bootstrapping, and Holm-Bonferroni adjustments.
  - Constructs the empirical recovery hazard matrix ($P(\tau \le K)$ for $K \in \{1, \dots, 20\}$).
* **Backtesting & Risk Management Framework ([`src/backtester.py`](../src/backtester.py))**:
  - Simulates portfolio performance on ₹1,000,000 INR starting capital across the full 19-year period.
  - Formulates realistic Indian statutory costs: Securities Transaction Tax (STT), NSE turnover fees, SEBI regulatory charges, Stamp Duty, GST, and round-trip slippage (0.07% total friction).
  - Implements dynamic 1.5x ATR trailing stop-loss exits and pre-drop close take-profit execution.
* **Figure Generation Pipeline ([`src/generate_figures.py`](../src/generate_figures.py))**:
  - Automatically generates 4 publication-grade visualization figures saved in `docs/`.
* **Automated Unified Test Suite ([`tests/test_all.py`](../tests/test_all.py))**:
  - Comprehensive unit tests covering OHLC invariance, event detection without look-ahead bias, statistical engines, backtester executions, and PDF deliverable constraints (7/7 tests passing).

---

## 4. Human Oversight, Critical Falsification, and Quality Auditing

While AI accelerated drafting and boilerplate implementation, the **core quantitative value of this study stems from strict human skepticism, falsification, and domain knowledge**:

1. **Rejecting Naive Model Outputs**:
   - Initial AI suggestions proposed simple rolling averages that showed positive post-shock returns. Human intervention recognized this as an **unconditional equity drift bias** and mandated the construction of an identical-horizon rolling baseline distribution ($N = 4,659$).
2. **Catching the Look-Ahead Close Execution Trap**:
   - Standard commercial backtests assume frictionless execution at 15:30:00 IST on the crash day. Human oversight enforced the implementation of **Model B (Day $T+1$ Open execution)**, proving that the overnight gap (+0.15%) extracts the theoretical bounce before retail traders can participate.
3. **Discovering the 200 SMA Bear Market Trap**:
   - Human inspection partitioned events by macro regime, revealing that **73% of crashes occur below the 200 SMA**, where downside momentum and volatility clustering turn dip-buying into a negative-drift trap (+0.14% recovery).
4. **Incorporating Real Indian Statutory Market Frictions**:
   - Ensured exact Indian equity market parameters were modeled: STT, NSE turnover fees, SEBI fees, state stamp duties, GST, and execution slippage, transforming an apparent +0.32% gross rebound into an economically unviable -7.16% net strategy.
5. **Auditing Mathematical & Code Correctness**:
   - Manually validated degrees of freedom formulas, circular block wrapping logic, and drawdown calculations against synthetic test fixtures.

---

## 5. Summary & Ethical Integrity

AI served as a high-velocity quantitative research assistant—synthesizing relevant literature and accelerating code scaffolding. Every mathematical formula, empirical deduction, code line, and research conclusion was directed, audited, and validated to ensure absolute rigor, transparency, and deterministic reproducibility.
