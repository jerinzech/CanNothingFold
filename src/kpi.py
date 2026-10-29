"""KPI module: consumes results/ CSVs and prints/saves the final business case.

Inputs (all produced by the notebooks):
- results/predicted_price.csv          predicted fair price of a Nothing foldable
- results/dl_predicted_price.csv      NN price cross-check (price uncertainty)
- results/segments.csv               segment profiles + foldable segment size
- results/pain_points.csv            ranked pain points
- results/sentiment_summary.csv      sentiment by model / tier / country
- results/rl_policy.csv              learned pricing policy: per-quarter price,
                                      units and margin
- results/rl_vs_fixed_margin.csv      RL policy margin vs fixed-price baseline
- results/rl_sensitivity.csv          elasticity x share sensitivity grid
- data/enrichment/enrichment_market.csv  global foldable market size (cited)

Computes:
- per-quarter and cumulative cashflow over the 8 launch quarters
- break-even unit volume and break-even quarter vs an assumed launch cost
- margin delta of the RL policy vs the best fixed price
- a go/no-go scorecard with every assumption labelled real vs assumed

Outputs:
- results/kpi_summary.csv
- figures/kpi_cashflow.png (cumulative cashflow curve with break-even line)

Run standalone:  .venv/bin/python src/kpi.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
ENRICHMENT = ROOT / "data" / "enrichment"
FIGURES = ROOT / "figures"

# --- documented assumptions (no public Nothing foldable program cost exists) --
UNIT_COST_PCT = 0.60          # unit cost as share of fair price (build plan)
LAUNCH_COST_M_USD = 150.0      # assumed upfront program cost (R&D + launch marketing)
LAUNCH_COST_SENSITIVITY_M = [100.0, 150.0, 300.0, 450.0]  # sensitivity range
SHARE_BASE = 0.01             # Nothing foldable share of segment (notebook 05)


def load_inputs() -> dict[str, pd.DataFrame]:
    files = {
        "predicted_price": RESULTS / "predicted_price.csv",
        "dl_predicted_price": RESULTS / "dl_predicted_price.csv",
        "segments": RESULTS / "segments.csv",
        "pain_points": RESULTS / "pain_points.csv",
        "sentiment_summary": RESULTS / "sentiment_summary.csv",
        "rl_policy": RESULTS / "rl_policy.csv",
        "rl_vs_fixed_margin": RESULTS / "rl_vs_fixed_margin.csv",
        "rl_sensitivity": RESULTS / "rl_sensitivity.csv",
        "market": ENRICHMENT / "enrichment_market.csv",
    }
    frames = {}
    for name, path in files.items():
        if not path.exists():
            raise FileNotFoundError(
                f"{path} not found. Run the notebooks first (see README run order).")
        frames[name] = pd.read_csv(path)
    return frames


def build_business_case(frames: dict[str, pd.DataFrame]) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (per-quarter cashflow table, key-value KPI summary table)."""
    pred = frames["predicted_price"].iloc[0]
    dl_pred = frames["dl_predicted_price"].iloc[0]
    policy = frames["rl_policy"]
    margin = frames["rl_vs_fixed_margin"]
    sens = frames["rl_sensitivity"]
    market = frames["market"]
    pain = frames["pain_points"]
    sentiment = frames["sentiment_summary"]

    fair_price = float(pred.predicted_price_usd)
    unit_cost = UNIT_COST_PCT * fair_price
    launch_price = float(policy.chosen_price.iloc[0])
    margin_per_unit = launch_price - unit_cost

    # --- per-quarter cashflow under the learned RL policy --------------------
    cashflow = policy[["launch_quarter", "t", "chosen_price", "units_q", "margin_musd"]].copy()
    cashflow = cashflow.rename(columns={"chosen_price": "price_usd",
                                        "units_q": "units",
                                        "margin_musd": "contribution_musd"})
    cashflow["cumulative_musd"] = cashflow.contribution_musd.cumsum()
    for cost in LAUNCH_COST_SENSITIVITY_M:
        cashflow[f"net_cashflow_cost_{cost:.0f}m"] = (
            cashflow.cumulative_musd - cost)
    cumulative_8q = float(cashflow.cumulative_musd.iloc[-1])

    # --- RL vs fixed headline ------------------------------------------------
    learned = margin.loc[margin.strategy == "q_learning (learned)"].iloc[0]
    best_fixed_row = margin[margin.strategy.str.startswith("fixed")].iloc[0]
    rl_delta = float(learned.mean_margin_musd) - float(best_fixed_row.mean_margin_musd)

    # --- break-even -----------------------------------------------------------
    break_even_units = LAUNCH_COST_M_USD * 1e6 / margin_per_unit
    base_net = cashflow[f"net_cashflow_cost_{LAUNCH_COST_M_USD:.0f}m"]
    be_quarters = {cost: None for cost in LAUNCH_COST_SENSITIVITY_M}
    for cost in LAUNCH_COST_SENSITIVITY_M:
        col = f"net_cashflow_cost_{cost:.0f}m"
        hit = cashflow.loc[base_net.name if False else cashflow[col] >= 0, "launch_quarter"]
        be_quarters[cost] = hit.iloc[0] if len(hit) else None
    base_be_quarter = be_quarters[LAUNCH_COST_M_USD]

    # share needed to break even within 8 quarters at base cost (margins are
    # ~linear in share — verified against rl_sensitivity.csv)
    share_be = SHARE_BASE * LAUNCH_COST_M_USD / cumulative_8q

    # --- context rows ----------------------------------------------------------
    foldable_segment = (frames["segments"].sort_values("mean_price_usd", ascending=False)
                        .iloc[0])
    top_pain = pain.iloc[0]
    overall_sentiment = sentiment.loc[sentiment.segment == "overall"].iloc[0]
    market_2025 = float(market.loc[market.year == 2025, "global_foldable_shipments_m"].iloc[0])

    # --- go / no-go scorecard ---------------------------------------------------
    checks = [
        ("positive contribution every quarter",
         bool((cashflow.contribution_musd > 0).all())),
        ("8-quarter contribution covers assumed launch cost ($150M)",
         cumulative_8q >= LAUNCH_COST_M_USD),
        ("launch price within model CI ($868-$1,650)",
         float(pred.ci90_low_usd) <= launch_price <= float(pred.ci90_high_usd)),
        ("learned policy beats best fixed price",
         rl_delta > 0),
        ("break-even share <= assumed share (1.0%)",
         share_be <= SHARE_BASE),
    ]
    passed = sum(ok for _, ok in checks)
    recommendation = "GO" if passed >= 4 else ("CONDITIONAL GO" if passed >= 3 else "NO-GO")

    rows = [
        # (key, value, unit, source)
        ("fair_price_usd", round(fair_price, 2), "USD", "notebook 02 random forest (real: ML estimate)"),
        ("fair_price_ci90_low_usd", round(float(pred.ci90_low_usd), 2), "USD", "notebook 02 bootstrap"),
        ("fair_price_ci90_high_usd", round(float(pred.ci90_high_usd), 2), "USD", "notebook 02 bootstrap"),
        ("dl_price_cross_check_usd", round(float(dl_pred.predicted_price_usd), 2), "USD",
         "notebook 03 NN — divergent extrapolation, documented as price risk"),
        ("unit_cost_usd", round(unit_cost, 2), "USD", "assumed 60% of fair price (build plan)"),
        ("launch_price_usd", launch_price, "USD", "notebook 05 RL policy, 2027Q1"),
        ("price_path_min_max_usd", f"{int(policy.chosen_price.min())}-{int(policy.chosen_price.max())}",
         "USD", "notebook 05 learned policy path"),
        ("margin_per_unit_usd", round(margin_per_unit, 2), "USD/phone", "launch price - unit cost"),
        ("addressable_foldable_market_m_units", market_2025, "M units/yr (2025)",
         "enrichment_market.csv (IDC/Omdia, cited)"),
        ("assumed_share_of_segment_pct", SHARE_BASE * 100, "%",
         "assumption (notebook 05 sensitivity 0.5-2%)"),
        ("units_per_quarter_mean", int(cashflow.units.mean()), "phones/quarter",
         "notebook 05 demand model (simulated)"),
        ("cumulative_8q_contribution_musd", round(cumulative_8q, 2), "M USD",
         "notebook 05 learned policy (simulated)"),
        ("best_fixed_price_baseline_musd", round(float(best_fixed_row.mean_margin_musd), 2), "M USD",
         "notebook 05 fixed $1,299"),
        ("rl_policy_margin_delta_musd", round(rl_delta, 2), "M USD",
         "learned policy minus best fixed (simulated)"),
        ("assumed_launch_cost_musd", LAUNCH_COST_M_USD, "M USD",
         "assumption; sensitivity 100/150/300/450"),
        ("break_even_units", int(round(break_even_units)), "phones",
         "launch cost / margin per unit (at launch price)"),
        ("break_even_quarter_base", base_be_quarter or "beyond 8 quarters", "-",
         "cumulative net cashflow >= 0 (base cost)"),
        ("break_even_share_pct", round(100 * share_be, 2), "%",
         "share needed to break even in 8 quarters at base cost"),
        ("foldable_listing_segment_share_pct_india", float(foldable_segment.share_pct), "%",
         f"notebook 02 premium cluster (n={int(foldable_segment.n)}), India-only"),
        ("top_pain_point", str(top_pain.pain_point), "-",
         f"notebook 04: {top_pain.share_of_negative_pct}% of negative reviews"),
        ("overall_sentiment_compound", float(overall_sentiment.mean_compound), "-",
         "notebook 04 VADER (synthetic-like corpus)"),
        ("go_no_go_checks_passed", f"{passed}/{len(checks)}", "-",
         "; ".join(f"{'PASS' if ok else 'FAIL'}: {name}" for name, ok in checks)),
        ("recommendation", recommendation, "-",
         "conditional on simulated demand; see README price-type and honesty notes"),
    ]
    summary = pd.DataFrame(rows, columns=["kpi", "value", "unit", "source"])
    return cashflow, summary


def main() -> None:
    frames = load_inputs()
    cashflow, summary = build_business_case(frames)

    RESULTS.mkdir(exist_ok=True), FIGURES.mkdir(exist_ok=True)
    cashflow.to_csv(RESULTS / "kpi_cashflow.csv", index=False)
    summary.to_csv(RESULTS / "kpi_summary.csv", index=False)

    # --- one-figure KPI chart: cumulative cashflow with break-even line -------
    fig, ax = plt.subplots(figsize=(9, 5))
    x = cashflow.launch_quarter
    ax.plot(x, cashflow.cumulative_musd, marker="o", color="#2b6cb0",
            label="cumulative contribution (learned RL policy)")
    ax.plot(x, cashflow[f"net_cashflow_cost_{LAUNCH_COST_M_USD:.0f}m"], marker="s",
            color="#2f855a", ls="--",
            label=f"net of assumed launch cost (${LAUNCH_COST_M_USD:.0f}M)")
    ax.axhline(0, color="black", lw=1)
    ax.axhline(LAUNCH_COST_M_USD, color="grey", ls=":", lw=1,
               label="assumed launch cost (break-even for contribution)")
    be = str(summary.loc[summary.kpi == "break_even_quarter_base", "value"].iloc[0])
    if be != "beyond 8 quarters":
        ax.annotate(f"break-even\n{be}", xy=(be, 0), xytext=(be, LAUNCH_COST_M_USD * 0.4),
                    fontsize=8, ha="center",
                    arrowprops=dict(arrowstyle="->", lw=0.8))
    ax.set_ylabel("M USD")
    ax.set_title("Nothing foldable 2027 launch — 8-quarter cashflow (simulated demand)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES / "kpi_cashflow.png", dpi=300)
    plt.close(fig)

    # --- console business case -------------------------------------------------
    print("=" * 72)
    print("CAN NOTHING FOLD?  —  KPI business case (src/kpi.py)")
    print("=" * 72)
    for _, row in summary.iterrows():
        print(f"{row.kpi:<42} {row.value} {row.unit}")
    print("-" * 72)
    print("Per-quarter cashflow under the learned RL policy:")
    print(cashflow.to_string(index=False))
    print("-" * 72)
    print("Full detail: results/kpi_summary.csv, results/kpi_cashflow.csv,")
    print("             figures/kpi_cashflow.png")
    print()
    print("Every demand-side number above is SIMULATED (see notebooks 05 honesty")
    print("notes); real-data anchors are the fair price, market size, competitor")
    print("median and sentiment profile. Assumptions: 60% unit cost, 1% share,")
    print("$150M launch cost (sensitivity 100/150/300/450).")


if __name__ == "__main__":
    main()
