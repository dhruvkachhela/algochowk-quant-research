# Video Presentation Script: NIFTY 50 Mean-Reversion Event Study
**Target Duration**: 2 Minutes 30 Seconds  
**Speaker**: Dhruv | **Challenge**: AlgoChowk Quant Engineer Intern

---

### [0:00 - 0:30] Slide 1: Introduction & Research Problem
* **Visual**: Title slide showing research question: *"After a significant one-day fall in NIFTY, does the market systematically recover over the next few trading days?"*
* **Speaking Script**:
  > *"Hi, my name is Dhruv. Today, I'm presenting our quantitative research into whether single-day declines in NIFTY 50 create an actionable mean-reversion edge. Rather than curve-fitting a winning backtest, our goal was to rigorously test this hypothesis against unconditional market drift, examine execution realism, model survival recovery rates, and see if the evidence holds under institutional scrutiny."*

---

### [0:30 - 1:05] Slide 2: Data Pipeline, Baseline & Survival Analysis
* **Visual**: Figure 3 (Event Study Trajectory Window [T-5 to T+10]) and Table 2 (Survival Recovery Probabilities).
* **Speaking Script**:
  > *"We validated 19 years of daily NIFTY data (4,664 trading days from 2007 to 2026). Defining a significant fall as a drop of 2% or more yielded exactly 200 events.
  >
  > While naive researchers celebrate that 5-day post-drop returns average +0.32%, the unconditional market naturally drifts up by +0.21% over any random 5-day period. The abnormal return is just +0.10% with a Welch p-value of 0.8031 and a 10,000-sample Block Bootstrap p-value of 0.7863. Furthermore, our survival analysis shows that by Day 5, the probability of fully recovering the drop is only 49%. More than half of all crash days remain unrecovered after a full trading week."*

---

### [1:05 - 1:45] Slide 3: Execution Realism & Regime Asymmetry
* **Visual**: Figure 1 (Close vs Open Entry Comparison) and Figure 2 (Bull vs Bear Regime Decomposition).
* **Speaking Script**:
  > *"Next, we challenged our results across execution and regime dynamics.
  >
  > First, execution timing: between the 3:30 PM close and 9:15 AM open, NIFTY experiences an average overnight gap of +0.15%. When entering realistically at next morning's open, the 5-day return drops to +0.16%—meaning the entire marginal bounce is locked overnight and inaccessible to intraday traders.
  >
  > Second, market regimes: when NIFTY is above its 200-day moving average, 3-day recovery averages +0.65%. But below the 200-day average, where 73% of all crashes occur, recovery collapses to +0.14% as downside momentum and volatility clustering dominate."*

---

### [1:45 - 2:25] Slide 4: Microstructure Conditioning & Risk-Managed Backtest
* **Visual**: Figure 4 (Empirical Recovery Probability Curve) and Backtest Comparison Table.
* **Speaking Script**:
  > *"We then tested whether market microstructure filters can rescue the trade. While volume surges alone did not improve outcomes, candlestick pin-bars with strong lower shadows—indicating buyer absorption off the lows—boosted 5-day returns to +1.57%.
  >
  > Finally, we simulated a portfolio net of Indian statutory taxes and 4 basis points of slippage. Blind 5-day holding lost -7.16% with a punishing -46% drawdown. However, adding dynamic risk controls—a 1.5x ATR stop-loss and taking profit upon reclaiming the pre-drop close—eliminated catastrophic left-tail losses and turned the strategy net positive."*

---

### [2:25 - 2:45] Slide 5: Conclusion & Quant Takeaway
* **Visual**: Summary of Conclusions & Architecture Diagram.
* **Speaking Script**:
  > *"In conclusion, we firmly reject the unconditioned hypothesis. A simple 2% drop in NIFTY is not an alpha signal: it is explained by normal drift, inaccessible via overnight gaps, and plagued by bear market momentum. An actionable quantitative strategy requires conditioning on lower shadow price absorption, trading strictly in bull regimes, and enforcing dynamic trailing stops. Thank you."*
