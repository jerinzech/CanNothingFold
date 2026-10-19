# Should Nothing Enter the Foldable Market?

University group project for *Fundamentals of Artificial Intelligence and Machine
Learning*. Five AI engines + a measured margin KPI produce a go/no-go business
recommendation for Nothing launching a foldable phone in 2027.

## Run order

```bash
pip install -r requirements.txt

# notebooks must run top-to-bottom (Kernel > Restart & Run All)
notebooks/01_data_prep.ipynb          # datasets, verification gate, is_foldable flag
notebooks/02_ml_price_segmentation.ipynb   # price regression + k-means segmentation
notebooks/03_dl_neural_network.ipynb       # feed-forward NN vs 02's baselines
notebooks/04_nlp_foldable_reviews.ipynb    # sentiment + topic modelling
notebooks/05_rl_pricing_agent.ipynb         # dynamic pricing agent (simulated)
notebooks/06_rnn_lstm_sentiment.ipynb      # monthly sentiment forecast

python src/kpi.py                     # final business case: break-even, margin, cashflow
```

## Dataset sources (verify each Kaggle slug before download; pin exact URLs here)

| File | Source |
|---|---|
| specs.csv | Kaggle: shraddha4ever20/smartphone-specifications-dataset |
| reviews.csv | Kaggle: masaladata/14-million-cell-phone-reviews (confirm 1.4M vs 14M) |
| reviews_global.csv | Kaggle: mohankrishnathalla/mobile-reviews-sentiment-and-specification |
| mobiles_2025.csv | Kaggle: abdulmalik1518/mobiles-dataset-2025 |
| sales_india.csv | Kaggle: yaminh/smartphone-sale-dataset |
| enrichment_market.csv | axis-intelligence.com foldable-phone-statistics (compiled, cited) |
| enrichment_wb.csv | World Bank DataBank (mobile penetration) |

Verification gate: records >1,000 for all datasets; features >=25 for specs.csv only.

## Layout

- `data/raw/` untouched downloads; `data/processed/` cleaned outputs;
  `data/enrichment/` market stats.
- `results/` every model output as CSV (graded requirement).
- `figures/` every chart as PNG (300 dpi).
- `src/kpi.py` standalone KPI module — the spine of the business-value section.

## Deadline

Everything in `project.zip` by 2 November 2026.
