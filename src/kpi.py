"""KPI module: consumes results/ CSVs and prints/saves the final business case.

Inputs (all produced by the notebooks):
- results/predicted_price.csv          predicted fair price of a Nothing foldable
- results/dl_vs_ml_comparison.csv     NN vs ML model comparison (price check)
- results/segments.csv                 segment profiles + foldable segment size
- results/sentiment_summary.csv        sentiment by model / tier / country
- results/pain_points.csv             ranked pain points with negative-review share
- results/rl_policy.csv                learned pricing policy (state -> price)
- results/rl_vs_fixed_margin.csv        RL policy margin vs fixed-price baseline

Computes:
- addressable units x realistic share x (price - unit cost) per quarter
- break-even unit volume
- projected margin and cashflow over 8 quarters
- margin delta of the RL policy vs fixed price

Outputs:
- results/kpi_summary.csv
- figures/kpi_cashflow.png (cumulative cashflow curve with break-even line)

Run standalone: python src/kpi.py
"""
