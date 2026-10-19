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

## Dataset sources (slugs verified 2026-10-19; place files in `data/raw/`)

| File to save as | Source | Notes |
|---|---|---|
| specs.csv | Kaggle: shraddha4ever20/smartphone-specifications-dataset | ships as `smartphones.csv`, 15,000 x 25 |
| reviews.csv | Kaggle: masaladata/14-million-cell-phone-reviews | 7 files `phone_user_review_file_1..7.csv` (~1.4M total); latest review May 2017 |
| reviews_global.csv | Kaggle: mohankrishnathalla/mobile-reviews-sentiment-and-specification | 50k reviews, 8 countries; **primary foldable corpus** |
| mobiles_2025.csv | Kaggle: abdulmalik1518/mobiles-dataset-2025 | launch prices PK/IN/CN/US/UAE + year |
| sales_india.csv | Kaggle: yaminh/smartphone-sale-dataset | ships as `Sales.csv`, ~3,114 rows, INR |
| enrichment_market.csv | axis-intelligence.com foldable-phone-statistics | compile key figures into CSV, cite source |
| enrichment_wb.csv | World Bank DataBank | mobile penetration |

reviews.csv ends May 2017 — foldables launched 2019, so it contains zero foldable
reviews. All foldable NLP work uses reviews_global.csv; reviews.csv is background only.

Verification gate: records >1,000 for all datasets; features >=25 for specs.csv only.

## Layout

- `data/raw/` untouched downloads; `data/processed/` cleaned outputs;
  `data/enrichment/` market stats.
- `results/` every model output as CSV (graded requirement).
- `figures/` every chart as PNG (300 dpi).
- `src/kpi.py` standalone KPI module — the spine of the business-value section.

## Deadline

Everything in `project.zip` by 2 November 2026.
