import os
import pymupdf

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_FILE = os.path.join(BASE_DIR, "docs", "research_note.pdf")

def create_research_note_pdf():
    doc = pymupdf.open()
    doc.new_page(width=595, height=842) # page 0
    doc.new_page(width=595, height=842) # page 1
    
    page1 = doc[0]
    page2 = doc[1]
    
    p1_lines = [
        "ALGOCHOWK QUANT ENGINEER INTERN CHALLENGE",
        "RESEARCH NOTE: POST-CRASH MEAN REVERSION IN NIFTY 50",
        "Candidate: Dhruv | Date: September 2026",
        "Dataset: NIFTY 50 Index Daily OHLCV (Sept 2007 - Sept 2026, 4,664 Trading Days)",
        "=" * 76,
        "",
        "1. EXECUTIVE SUMMARY & CORE HYPOTHESIS",
        'Hypothesis Investigated: "After a significant one-day fall in NIFTY, the market tends',
        'to recover over the next few trading days."',
        "",
        "Key Quantitative Findings:",
        "1. Statistical Insignificance: After a drop <= -2.0% (N=200), average 5-day forward return",
        "   is +0.32% vs an unconditional baseline of +0.21% (Abnormal Return = +0.10%, Welch",
        "   t = +0.25, p = 0.8031; 10,000-sample Block Bootstrap p = 0.7863). The bounce is",
        "   statistically indistinguishable from random market drift.",
        "2. Survival Hazard Rate: By Day 1, probability of 100% recovery is only 14.5%. By Day 5,",
        "   full recovery probability is 49.0%. Over 51% of all crash days remain unrecovered",
        "   after an entire trading week.",
        "3. Execution Trap: Mean overnight gap is +0.15% (58% positive). When entering at Day T+1",
        "   Open, 5-day return drops to +0.16% (Abnormal Return = -0.06%, p = 0.8836). The edge is",
        "   locked in the overnight gap and cannot be captured during market hours.",
        "4. Severe Regime Asymmetry: In bull regimes (Price > 200 SMA), 3-day recovery is +0.65%",
        "   (59.3% win rate). In bear regimes (Price < 200 SMA, 73% of all crashes), recovery",
        "   collapses to +0.14% (52.7% win rate) due to downside momentum and volatility clustering.",
        "5. Economic Non-Viability: Net of 0.07% Indian statutory costs (STT, NSE fees, 4 bps",
        "   slippage), blind 5-day holding loses -7.16% with a -46.18% maximum drawdown.",
        "",
        "-" * 76,
        "2. EXPERIMENTAL DESIGN & DEFINITIONS",
        "* Event Definition: Daily Close-to-Close Return <= -2.0% (N = 200).",
        "* Baseline Model: Unconditional rolling H-day returns across all 4,664 days.",
        "* Dual Execution Models: Model A (Day T Close MOC) vs Model B (Day T+1 Open 9:15 AM).",
        "* Out-of-Sample Split: In-Sample 2007-2018 (N=149) vs Out-of-Sample 2019-2026 (N=51).",
        "",
        "-" * 76,
        "3. EMPIRICAL RESULTS & HYPOTHESIS TESTING",
        "Table 1: Benchmark Event Returns vs Unconditional Baseline (N = 200)",
        "-" * 76,
        "Horizon | Baseline Mean | Model A Mean | Abnormal | Welch t (p-val) | Boot p | Sig?",
        "  1d    |     +0.04%    |    +0.11%    |  +0.06%  |  +0.35 (0.7291) | 0.4804 | Fail",
        "  2d    |     +0.09%    |    +0.09%    |  +0.00%  |  +0.01 (0.9946) | 0.9925 | Fail",
        "  3d    |     +0.13%    |    +0.28%    |  +0.15%  |  +0.47 (0.6405) | 0.5426 | Fail",
        "  5d    |     +0.21%    |    +0.32%    |  +0.10%  |  +0.25 (0.8031) | 0.7863 | Fail",
        " 10d    |     +0.42%    |    +0.60%    |  +0.18%  |  +0.34 (0.7364) | 0.7546 | Fail",
        "-" * 76,
        "                                                              [Continued on Page 2...]"
    ]
    
    p2_lines = [
        "[Page 2: AlgoChowk Research Note - Dhruv]",
        "=" * 76,
        "",
        "Table 2: Survival Analysis (Hazard Rate of Recovery by Day K)",
        "-" * 76,
        "Elapsed Days (K) | Cumulative Prob of 50% Recovery | Cumulative Prob of 100% Recovery",
        "     Day 1       |              43.5%               |              14.5%",
        "     Day 2       |              59.0%               |              26.0%",
        "     Day 3       |              65.5%               |              39.0%",
        "     Day 5       |              72.0%               |              49.0%",
        "     Day 10      |              81.5%               |              65.5%",
        "     Day 20      |              85.5%               |              74.5%",
        "-" * 76,
        "",
        "4. CRITICAL FALSIFICATION & RISK ANALYSIS",
        "",
        "1. The 200 SMA Bear Market Trap:",
        "   73% of large drops occur below the 200-day moving average. In bear markets, one-day",
        "   falls exhibit severe downside momentum and volatility clustering rather than mean",
        "   reversion. Dip-buying during bear regimes causes catastrophic compounding losses.",
        "",
        "2. Microstructure Findings (Capitulation vs Absorption):",
        "   * Volume Climax alone (> 1.5x 20d mean): 5-day return is -1.34% (N=15). Volume surges",
        "     reflect institutional liquidation rather than exhaustion.",
        "   * Pin-bar Lower Shadow Absorption: 5-day return is +1.57% (N=25). Rebound occurs only",
        "     when buyers step in before the close to defend intraday lows.",
        "",
        "3. Backtest Simulation (1,000,000 INR Capital, Net of 0.07% Indian Friction):",
        "   * Model A (Close Entry, Blind 5d Exit): Net Return: -7.16% | Max Drawdown: -46.18%",
        "   * Model B (Open Entry, Blind 5d Exit):  Net Return: -16.71% | Max Drawdown: -45.75%",
        "   * Risk-Managed (1.5x ATR Stop + TP):    Net Return: +0.82%  | Win Rate: 54.4%",
        "",
        "-" * 76,
        "5. FINAL CONCLUSION & QUANT RECOMMENDATION",
        "",
        "The empirical evidence FIRMLY REJECTS the unconditioned hypothesis:",
        "1. Post-drop forward returns are statistically indistinguishable from baseline market drift",
        "   across all tested horizons (p > 0.60).",
        "2. Survival analysis shows over 51% of crashes remain unrecovered after 5 trading days.",
        "3. The marginal edge is trapped in overnight gaps and destroyed by bear market momentum.",
        "4. After standard Indian statutory costs, unconditioned mean reversion is economically",
        "   unviable.",
        "",
        "Quantitative Recommendation:",
        "An actionable trading model must condition entries on lower shadow price absorption,",
        "restrict trades strictly to bull regimes (Price > 200 SMA), and enforce 1.5x ATR",
        "trailing stops.",
        "=" * 76
    ]
    
    y = 50
    for line in p1_lines:
        page1.insert_text((45, y), line, fontsize=9, fontname="courier")
        y += 15.5
        
    y = 50
    for line in p2_lines:
        page2.insert_text((45, y), line, fontsize=9, fontname="courier")
        y += 15.5
        
    doc.save(PDF_FILE)
    print(f"[OK] Generated clean 2-page PDF: {PDF_FILE}")

if __name__ == "__main__":
    create_research_note_pdf()
