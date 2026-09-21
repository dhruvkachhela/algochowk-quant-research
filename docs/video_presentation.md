# Video Presentation Script: NIFTY 50 Mean-Reversion Event Study
**Target Duration**: 2 Minutes 30 Seconds  
**Speaker**: Dhruv | **Challenge**: AlgoChowk Quant Engineer Intern

---

### [0:00 - 0:30] Slide 1: Introduction & Research Problem
* **Visual**: Title slide showing research question: *"After a significant one-day fall in NIFTY, does the market systematically recover over the next few trading days?"*
* **Speaking Script**:
  > *"Hi, my name is Dhruv. Today, I'm presenting our quantitative investigation into whether sharp single-day declines in NIFTY 50 create a statistically significant, tradable mean-reversion opportunity. Rather than optimizing for a high-return backtest, our goal was to rigorously test this hypothesis against unconditional market drift, examine execution realism, and determine whether the evidence deserves to be believed."*

---

### [0:30 - 1:05] Slide 2: Data Pipeline, Experimental Design & Baseline
* **Visual**: Split slide showing data validation metrics (4,664 trading days from 2007 to 2026) and Table 1 (Event Returns vs Unconditional Baseline).
* **Speaking Script**:
  > *"We sourced and verified 19 years of continuous daily NIFTY data, spanning from 2007 through September 2026, encompassing the 2008 crash, 2020 COVID shock, and 2024 election volatility. We defined a significant fall as a single-day drop of 2% or more, which occurred 200 times.*
  >
  > *A critical error in naive research is ignoring unconditional upward drift. Over any random 5-day period, NIFTY naturally gains +0.21%. While post-drop 5-day returns averaged +0.32%, this represents a tiny abnormal return of just +0.10%. Using a two-sample Welch t-test and a 10,000-sample Circular Block Bootstrap, the p-value was 0.8031, confirming that this bounce is statistically indistinguishable from random noise."*

---

### [1:05 - 1:45] Slide 3: Falsification, Regime Breakdown & Overnight Gap
* **Visual**: Figure 1 (Bar chart of Close vs Open Entry) and Figure 2 (Regime Plot: Bull Price > 200 SMA vs Bear Price < 200 SMA).
* **Speaking Script**:
  > *"To challenge our results, we tested two critical failure modes:*
  >
  > *First, execution timing. If we enter at Day T Close, we assume we knew the closing price before market close. If we instead enter realistically at next morning's 9:15 AM Open, the 5-day return drops to +0.16%—meaning the entire marginal bounce happens overnight in the opening gap.*
  >
  > *Second, market regimes. When NIFTY is above its 200-day moving average, dips bounce by +0.65% over 3 days. But when below the 200-day average, where 73% of large drops occur, recovery collapses to +0.14% due to severe downside momentum and volatility clustering."*

---

### [1:45 - 2:25] Slide 4: Realistic Backtest & Multiplicity Correction
* **Visual**: Figure 3 (Equity curve vs Buy & Hold) and Table 2 (Holm-Bonferroni Sensitivity Grid).
* **Speaking Script**:
  > *"We evaluated sensitivity across thresholds from -1.0% to -3.0%. After applying the Holm-Bonferroni correction for multiple testing, not a single parameter configuration was statistically significant.*
  >
  > *Finally, we simulated an event-driven portfolio starting with 10 lakh rupees, incorporating realistic Indian statutory costs—STT, exchange turnover fees, and 4 basis points of round-trip slippage. Over 19 years, the unconditioned mean-reversion strategy yielded a negative CAGR of -0.39% with a maximum drawdown of -46.18%, severely underperforming buy-and-hold."*

---

### [2:25 - 2:45] Slide 5: Conclusion & Research Insights
* **Visual**: Key Takeaways & Recommendations slide.
* **Speaking Script**:
  > *"In conclusion, we firmly reject the hypothesis that a simple one-day fall in NIFTY generates an actionable edge. The apparent bounce is explained by structural market drift, concentrated in inaccessible overnight gaps, and destroyed by bear market momentum and transaction frictions. A viable quant strategy would require multi-factor conditioning, such as India VIX term-structure inversion restricted strictly to bull regimes. Thank you."*
