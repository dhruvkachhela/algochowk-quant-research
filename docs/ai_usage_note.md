# AI Usage Note: Quantitative Research & Experimental Validation
**Author**: Dhruv | **Assignment**: AlgoChowk Quant Engineer Intern Challenge

---

### 1. AI Tools Used
* **AI Models / Assistants**: Antigravity Assistant (Google DeepMind) & Gemini 3.7.
* **Environment**: Local Python 3.13 runtime with Pandas, NumPy, SciPy, statsmodels, and Matplotlib.

---

### 2. How AI Tools Were Used
1. **Pipeline Scaffolding**: Generated modular class templates (`DataValidator`, `EventDetector`, `StatisticalEngine`, `EventBacktester`) and automated test cases.
2. **Deterministic Script Writing**: Used AI to write Python scripts for downloading clean OHLCV data from Yahoo Finance and executing Welch's t-tests, Mann-Whitney U tests, circular block bootstrapping, and Holm-Bonferroni corrections.
3. **Drafting Documentation**: AI structured the tables and formatted markdown summaries based on empirical numbers produced by our deterministic engine.

---

### 3. Decisions Made Independently
1. **Hypothesis Formulation & Falsification Design**: I chose to treat this investigation strictly as a falsification exercise rather than an attempt to manufacture a winning backtest. I formulated the research question around unconditional baseline drift comparison.
2. **Dual Execution Models**: I recognized that executing at Day T Close assumes knowing the close before market shutdown. I demanded the explicit inclusion of Model B (Entry at Day T+1 Open) to eliminate look-ahead bias.
3. **Multiplicity Penalty**: Rather than presenting individual cherry-picked thresholds, I enforced a full parameter grid (-1.0% to -3.0%) evaluated with Holm-Bonferroni step-down corrections.
4. **Market Regime Conditioning**: I mandated splitting events by the 200-day Simple Moving Average to investigate whether mean-reversion is an independent signal or merely a byproduct of structural bull markets.

---

### 4. Suggestions Changed or Disagreed With
1. **Initial Flawed Close-to-Close Assumption**: AI initially proposed calculating returns using simple close-to-close series without flagging that trade entry at Day T Close is impossible without a Market-On-Close order. I changed this to benchmark both MOC with slippage and next-morning Open execution.
2. **Rejection of Machine Learning / Black-Box Overfitting**: AI suggested testing Random Forests or Deep Learning for price prediction. I firmly rejected this approach, recognizing that 200 event observations in 19 years would lead to extreme overfitting, and that institutional quant research requires statistical hypothesis testing and p-values, not black-box curve fitting.

---

### 5. Incorrect AI Suggestions Identified
1. **Simple I.I.D. Bootstrap vs Autocorrelation**: AI initially generated a standard random-sample bootstrap that drew isolated single days from history. I pointed out that market returns exhibit volatility clustering, making standard i.i.d. draws inaccurate. I required the implementation of a **Circular Block Bootstrap** with 5-day blocks to preserve historical autocorrelation.
2. **Ignoring Statutory Friction in Futures/ETFs**: AI initially assumed zero friction. I corrected this by incorporating real Indian statutory charges (STT on sell side, NSE transaction turnover charges, SEBI turnover fees, GST) and a 4 bps round-trip bid-ask slippage.

---

### 6. Key Learnings
* **The Danger of Unconditional Drift**: An average positive return after a market drop is completely meaningless unless benchmarked against unconditional rolling windows.
* **Downside Momentum Dominates Bear Regimes**: 73% of extreme one-day falls occur in bear markets (Price < 200 SMA), where prices continue to fall rather than rebound.
* **Execution Reality Destroys Marginal Alphas**: The minor positive edge observed in naive backtests is captured almost entirely by the overnight gap, leaving zero tradable alpha for intraday traders.
