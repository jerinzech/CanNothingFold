# Should Nothing Enter the Foldable Market?

University group project for *Fundamentals of Artificial Intelligence and Machine
Learning*. Five AI engines plus a measured margin KPI produce a go/no-go business
recommendation for Nothing launching a foldable phone in 2027.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate          # or use .venv/bin/python directly
pip install -r requirements.txt

# Build the enrichment tables (network only for the optional store refresh)
python src/collect_nothing_prices.py   # optional: refresh the official snapshot
python src/fetch_worldbank.py          # uses cached raw JSON when present
python src/build_enrichment.py         # compiled prices, foldables, market tables
python src/build_manifest.py           # raw-file hashes and row/column inventory

# Run notebook 01 top-to-bottom
python -m jupyter nbconvert --to notebook --execute \
  notebooks/01_data_prep.ipynb --inplace
```

Then run notebooks 02–06 from a clean kernel (`Kernel > Restart & Run All`).

## Run order

```text
notebooks/01_data_prep.ipynb                  datasets, verification gate, cleaned outputs
notebooks/02_ml_price_segmentation.ipynb      price regression + k-means segmentation
notebooks/03_dl_neural_network.ipynb          feed-forward NN vs 02's baselines
notebooks/04_nlp_foldable_reviews.ipynb       sentiment + topic modelling
notebooks/05_rl_pricing_agent.ipynb           dynamic pricing agent (simulated)
notebooks/06_rnn_lstm_sentiment.ipynb         monthly sentiment forecast

python src/kpi.py                             final business case: break-even, margin, cashflow
```

## Data foundation

Full verified inventory, shapes, quirks and corrections:
**[`data/datasets.md`](data/datasets.md)**.

### Canonical raw files (`data/raw/`)

| File | Source | Role |
|---|---|---|
| `phone_information_2024.csv` | Kaggle: willianoliveiragibin/phone-information-2024 | **Core** specs + UK/DE/US marketplace prices (local currency); 1,715 × 31 |
| `phones_2024.csv` | Kaggle: jakubkhalponiak/phones-2024 | Backup core, USD-only price |
| `mobiles_2025.csv` | Kaggle: abdulmalik1518/mobiles-dataset-2025 | 5-country launch-price **comparator**; no Nothing rows; Latin-1 |
| `gsmarena_prices.csv` | Kaggle: beridzeg45/gsmarena-smartphones | Global USD launch validation |
| `sales_india.csv` | Kaggle: yaminh/smartphone-sale-dataset | India-only sales segmentation |
| `reviews_global.csv` | Kaggle: mohankrishnathalla/mobile-reviews-sentiment-and-specification | Primary foldable review corpus |
| `phone_user_review_file_1..6.csv` | Kaggle: masaladata/14-million-cell-phone-reviews | Background reviews, ends May 2017 |
| `specs_india_2026.csv` | Kaggle: suresh2837/...20082026 | India retail supplement |
| `specs_india_2025_basic.csv` | Kaggle: rohsanyadav/smartphones-dataset | India retail supplement |
| `specs_india_2025.csv` | Kaggle: vashisthrahul13/mobile-price-and-specs-2025 | India retail supplement |
| `spain_prices.csv` | Kaggle: juanmerinobermejo/smartphones-price-dataset | Spain EUR retail |
| `specs_india_2026_alt.csv` | Kaggle: abhishekmondal/...2026 | Unverified India holdout; do not publish |
| `nothing_official_prices_2026-10-29.csv` | Nothing official stores | Current-price snapshot, 15 markets; **not launch prices** |
| `worldbank_*.json` | World Bank API | 8 indicators × 20 countries × 2015–2025 |

The original synthetic `specs.csv` is archived at
`data/raw/archive/specs_synthetic.csv` and must not be used. D03 is a competitor
comparator: it contains **zero Nothing models**, so Nothing launch prices live in
`data/enrichment/nothing_launch_prices_manual.csv`.

### Compiled enrichment (`data/enrichment/`)

| File | Rows × cols | Contents |
|---|---:|---|
| `price_by_country.csv` | 19,347 × 22 | Main long price table: model × country × source × price type |
| `foldable_prices.csv` | 271 × 22 | Foldable subset for notebooks 02–04 |
| `nothing_prices.csv` | 182 × 22 | Nothing-only prices across all sources |
| `nothing_prices_template.csv` | 104 × 10 | 13 models × 8 target countries; 30 `need` cells |
| `nothing_official_current.csv` | 123 × 11 | Official store snapshot, 15 markets |
| `nothing_launch_prices_manual.csv` | 24 × 8 | Cited launch anchors, 8 models / 4 markets |
| `enrichment_wb.csv` | 220 × 11 | World Bank country-year panel |
| `enrichment_wb_latest.csv` | 20 × 11 | Latest value per country |
| `enrichment_market.csv` | 3 × 8 | Global 2023–2025 market seed |
| `enrichment_market_country.csv` | 18 × 9 | Country market seed; 7 `to_fill` |

### Price-type rules

Never mix these in a ratio or chart without grouping by `price_type`:

- `official_launch` — original MSRP. D03 rows are competitors; manual anchors are Nothing.
- `official_current` — current Nothing store price on 2026-10-29 (not launch).
- `marketplace` — D01 Amazon/brand-store listings, median per model × country.
- `retail` — D08/D11/D27/D29 discounted retail snapshots.
- `retail_unverified` — D14 holdout; excluded from verified outputs.

Country indices in `results/country_price_index.csv` are **within-model ratios versus
the US**, grouped by segment and price type. The fixed FX table (`FX_ASOF =
2026-10-29`) is documented in `data/datasets.md`; `USD 0.92 EUR` is an explicit
assumption, not a live rate.

## Outputs

- `results/country_price_index.csv` — 35 grouped country/segment/price-type ratios
- `results/data_verification.csv` — verification gate table (graded requirement);
  passes for all **hard** datasets, with soft warnings for supplementary ones
  (D03, D14, `nothing_prices.csv`, `enrichment_wb.csv`) that are gated through the
  compiled tables instead
- `results/data_quality_summary.csv`, `results/data_missingness.csv`
- `data/processed/*_clean.csv` — notebook 01 outputs (executed 2026-10-29):

| File | Rows × cols | Contents |
|---|---:|---|
| `phone_models_clean.csv` | 1,715 × 50 | D01 core specs + `is_foldable` flag + FX-validated USD |
| `mobiles_clean.csv` | 930 × 37 | D03 5-country launch comparator (no Nothing rows) |
| `sales_india_clean.csv` | 3,006 × 16 | India sales; duplicates/missing prices removed |
| `reviews_global_clean.csv` | 50,000 × 38 | Primary foldable NLP corpus |
| `reviews_background_clean.csv` | 200,000 × 9 | Deterministic sample of the 1.42M background reviews |
| `spain_prices_clean.csv` | 1,816 × 13 | Spain EUR retail |
| `price_by_country_clean.csv` | 19,347 × 24 | Enrichment long table + joins |
| `nothing_prices_clean.csv` | 182 × 24 | Nothing prices, all sources/price types |
| `foldable_prices_clean.csv` | 271 × 24 | Foldable subset |

- `results/` — every model output as CSV (graded requirement)
- `figures/` — every chart as PNG (300 dpi)

## Layout

- `data/raw/` untouched downloads; `data/processed/` cleaned outputs;
  `data/enrichment/` compiled tables.
- `src/collect_nothing_prices.py` — official-store snapshot scraper.
- `src/fetch_worldbank.py` — World Bank API downloader/builder.
- `src/build_enrichment.py` — single source of truth for price/model normalisation,
  FX conversion and the compiled tables.
- `src/build_manifest.py` — raw-file sha256/row/column inventory
  (`data/raw/MANIFEST.csv`, 33 entries incl. the archived D16 synthetic specs).
- `src/kpi.py` — standalone KPI module (business-value spine).

## Deadline

Everything in `project.zip` by **2 November 2026**.
