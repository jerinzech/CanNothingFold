# Build Plan — "Should Nothing Enter the Foldable Market?"

## 1. Context

You are building a university group project (end-to-end AI solution) for the course
*Fundamentals of Artificial Intelligence and Machine Learning*. The final deliverable is a
go / no-go business recommendation for the company Nothing entering the foldable smartphone
market, backed by five AI engines and a measured margin KPI.

- **Role**: data & AI consultants advising Nothing.
- **Business question**: should Nothing launch a foldable phone in 2027? Reframed into
  estimable sub-questions (price point, target segment, consumer pain points, pricing policy).
- **Tooling**: Python + Jupyter notebooks only (professor approved replacing Orange).
  No Orange required.
- **Hard deadline**: everything in `project.zip` by 2 November 2026.
- **Grading bar to hit**: three core engines used in depth + the two optional Python
  extensions (RL, RNN/LSTM) + a convincing business story with KPIs.

## 2. Repository structure

The repository root (`CanNothingFold/`) IS the project folder — no nested `project/`
level:

```
CanNothingFold/            # repo root = project root
  README.md                  # run order, dataset sources, requirements
  requirements.txt
  .gitignore                 # excludes .DS_Store, .venv, data/raw, data/processed
  build_plan.md              # this document
  data/
    raw/                     # downloaded datasets, untouched (git-ignored)
      MANIFEST.csv             # sha256/rows/cols provenance inventory (33 entries)
      archive/                 # screened-out originals (D16 synthetic specs)
    processed/               # cleaned, joined, feature-engineered outputs (git-ignored)
    enrichment/              # compiled price/market/World Bank tables (tracked)
  notebooks/
    01_data_prep.ipynb
    02_ml_price_segmentation.ipynb
    03_dl_neural_network.ipynb
    04_nlp_foldable_reviews.ipynb
    05_rl_pricing_agent.ipynb
    06_rnn_lstm_sentiment.ipynb
  src/
    collect_nothing_prices.py  # official-store current-price snapshot scraper
    fetch_worldbank.py         # World Bank API downloader/builder
    build_enrichment.py        # single source of truth: normalisation, FX, compiled tables
    build_manifest.py          # raw-file sha256/row/column inventory
    kpi.py                     # break-even / margin model
  results/                   # all model outputs saved as CSV (graded requirement)
  figures/                   # all charts exported for report and slides
```

Rules: every notebook runs top-to-bottom on a clean machine (`Kernel > Restart & Run All`
must succeed). Every model output is saved to `results/` as CSV. Every chart is also
exported to `figures/` as PNG (300 dpi).

## 3. Data acquisition (notebook 01)

> **Superseded 2026-10-29:** the verified dataset inventory and final decisions live in
> [`data/datasets.md`](data/datasets.md). In particular, the synthetic `specs.csv` is
> archived; D01 `phone_information_2024.csv` is the core specs/price table, D03 is a
> competitor launch comparator with zero Nothing rows, and Nothing launch prices are
> hand-collected in `data/enrichment/nothing_launch_prices_manual.csv`. The steps below
> describe the original plan and are kept for context.
>
> **Status 2026-10-29 — notebook 01 is built and executed** (29 cells, clean
> `Restart & Run All`). Implementation differs from the original plan in three ways:
> 1. Prices are standardised to **USD** with the fixed FX table (`FX_ASOF = 2026-10-29`),
>    not EUR; D01's local-currency prices are retained alongside.
> 2. The verification gate is **hard for core datasets only** (records >1,000; features
>    ≥25 for the specs table). Supplementary tables (D03, D14, `nothing_prices.csv`,
>    `enrichment_wb.csv`) fail the raw row gate by design and are gated through the
>    compiled tables instead — recorded as soft warnings, not failures.
> 3. Enrichment joins consume the compiled tables in `data/enrichment/` (see
>    `src/build_enrichment.py`), not a single ad-hoc market CSV.
>
> Outputs: 9 `data/processed/*_clean.csv` files plus
> `results/data_verification.csv`, `results/data_quality_summary.csv` and
> `results/data_missingness.csv` (shapes in the README).

Download these public datasets into `data/raw/` (verify each Kaggle slug resolves before
writing notebook 01 around it — pin exact download URLs in the README; note the
`masaladata` dataset name says 14M while the plan assumes 1.4M, confirm which):

| File | Dataset | Source |
|---|---|---|
| specs.csv | Smartphone Specifications Dataset — 15,000 records, 25 attributes, 2015–2025 | Kaggle: shraddha4ever20/smartphone-specifications-dataset |
| reviews.csv | 1.4M cell phone reviews, 720 models | Kaggle: masaladata/14-million-cell-phone-reviews |
| reviews_global.csv | Global Mobile Reviews 2025 — 50k reviews, 8 countries | Kaggle: mohankrishnathalla/mobile-reviews-sentiment-and-specification |
| mobiles_2025.csv | Mobiles Dataset 2025 — launch prices PK/IN/CN/US/UAE | Kaggle: abdulmalik1518/mobiles-dataset-2025 |
| sales_india.csv | Smartphone Sales Dataset — India | Kaggle: yaminh/smartphone-sale-dataset |
| enrichment_market.csv | Foldable statistics 2026 (shipments, share, revenue multiples) | axis-intelligence.com foldable-phone-statistics (compile key figures into CSV, cite source) |
| enrichment_wb.csv | Mobile penetration, World Development Indicators | World Bank DataBank |

**Verified dataset facts (checked 2026-10-19, before building notebook 01):**
- All six Kaggle slugs resolve. `specs.csv` is 15,000 rows x 25 columns (file ships as
  `smartphones.csv`; price column spans 1–15000 in a near-uniform distribution — treat
  currency as an assumption to verify on first load).
- `reviews.csv` ships as 7 files (`phone_user_review_file_1..7.csv`, ~1.4M reviews total).
  **CRITICAL: its latest review is May 2017.** The first foldable shipped in 2019, so this
  dataset contains ZERO foldable reviews by construction.
- Consequence for the engines: **reviews_global.csv is the PRIMARY foldable review corpus**
  (50k reviews, 8 countries, includes Galaxy Z Flip and Razr 40). reviews.csv serves only
  as a general market-sentiment background corpus and for the record-count gate. Notebook
  06's monthly sentiment series must be built from reviews_global.csv.
- `sales_india.csv` ships as `Sales.csv` (~3,114 rows, prices in INR).

**Verification gate (graded requirement — do not skip):** after loading each dataset,
assert and print record count and feature count, then apply two separate thresholds:

- **Record count >1,000** — applies to all core datasets.
- **Feature count >=25** — applies to `specs.csv` only (the dataset is described as
  25 attributes, so a strict `>` would fail on the flagship dataset). Review and sales
  datasets naturally have few columns (5–8 features is normal for review data); requiring
  25 features there would trigger false failures and unnecessary backup swaps.

If a dataset fails its applicable thresholds, swap in the backup (reviews_global.csv is the
NLP backup; a Kaggle smartphone specs alternative is divyamkhetan/comprehensive-smartphone-
specifications-dataset). Print a verification table and save it to
`results/data_verification.csv`.

Notebook 01 must then:
1. Clean all core datasets: missing values, extreme values/outliers (IQR rule), duplicate models.
2. Convert categoricals to numeric (brand, country one-hot or target encoding).
3. Standardize prices to EUR (fixed conversion table, documented).
4. Create a `is_foldable` flag from model names — the join key for the whole project.
   Match on word boundaries against: `fold`, `flip`, `razr`. Do NOT use substring
   matching (avoids false hits like "folder") and do NOT match `duo` (Microsoft
   Surface Duo is a dual-screen device, not a folding-panel one; keep an exclusion
   note in the notebook).
5. Join enrichment data (market growth by year, country penetration) onto the main spec table.
6. Save cleaned outputs to `data/processed/` and a data-quality summary (rows in/out,
   missingness per column) to `results/`.

## 4. Engine 1 — Machine Learning (notebook 02)

Task A — **Price regression**: predict launch price from specs (numeric + encoded brand).
- Models: LinearRegression, RandomForestRegressor (sklearn).
- Splits: 5-fold cross-validation, report MSE, MAE, R².
- Feature importance: permutation importance, top 10 chart.
- Business output: predict the fair price of a hypothetical Nothing foldable (define a spec
  row: top-tier processor, foldable form factor, Nothing brand encoded as average challenger
  brand). Save prediction + confidence interval (RF quantile or bootstrap) to `results/predicted_price.csv`.

Task B — **Segmentation**: k-means on sales_india.csv features (price, rating, discount, brand tier).
- Standardize features first. Use elbow/silhouette to choose k (3–5).
- Output: segment profiles table + scatter plot colored by cluster.
- Business output: which segment foldables fall into and its size. Save `results/segments.csv`.

## 5. Engine 2 — Deep Learning (notebook 03)

- Feed-forward network (Keras Sequential or sklearn MLPRegressor) on the SAME price task as
  notebook 02 for a controlled comparison.
- Architecture: 2–3 hidden layers, ReLU, early stopping, small dropout. Standardized inputs.
- Compare NN vs linear regression vs random forest on the same CV folds: table of MSE/R².
- Business output: does the non-linear model beat the linear one, and does that change the
  predicted foldable price? Save `results/dl_vs_ml_comparison.csv` and the predicted price
  for the same hypothetical foldable row.

## 6. Engine 3 — NLP (notebook 04)

- Filter the foldable review corpus from **reviews_global.csv (primary — it is the only
  dataset that can contain foldables; reviews.csv ends May 2017)**, using the
  `is_foldable` mapping. Use reviews.csv only as a general background corpus if needed.
  Print and record the corpus size honestly.
- Pipeline: lowercasing, stopword removal, lemmatization (nltk or spaCy), tokenization.
- **Sentiment**: VADER or a fine-tuned-off-the-shelf sentiment model; sentiment distribution
  overall, by model, by price tier, by country. Save `results/sentiment_summary.csv`.
- **Topic modelling**: LDA (gensim or sklearn) on the foldable complaint subset; 5–8 topics;
  label them manually (expected: crease/durability, price, weight, battery, screen).
- Charts: sentiment by model (bar), sentiment by price tier, top-topics table, word cloud
  of negative reviews.
- Business output: ranked list of pain points a Nothing foldable must solve, with the share
  of negative reviews each topic explains. Save `results/pain_points.csv`.

## 7. Engine 4 — Reinforcement Learning (notebook 05)

Build a dynamic pricing agent. Simulated environment (state this limitation honestly):

- **Environment** (custom gymnasium `Env` or hand-rolled): one episode = 8 launch quarters.
  - State: current price tier, time step, competitor average price (from data), current
    market sentiment score (from notebook 04 outputs).
  - Action: choose price from {899, 999, 1099, 1199, 1299} EUR.
  - Demand model: base demand for the foldable segment (from enrichment market data)
    scaled by Nothing's realistic share, multiplied by a price-elasticity response.
    The elasticity CANNOT be fit from notebook 02 (which predicts price from specs,
    not demand from price — no foldable demand-vs-price data exists in these
    datasets). Treat elasticity as a documented, cited assumption (e.g. a linear
    penalty when price exceeds the predicted fair price from notebook 02); state
    the assumed value and a sensitivity range in the notebook.
  - Reward: units × (price − unit_cost), with unit_cost set to 60% of the predicted fair
    price (document the assumption; cite that foldables earn ~3.9x the revenue of an average
    smartphone as market context).
- **Agent**: tabular Q-learning first (epsilon-greedy, ~10k episodes). If time allows, add a
  small DQN (PyTorch) and compare learning curves.
- **Outputs**: learned pricing policy (state→price table), reward curve, and the headline
  number — cumulative margin under the learned policy vs. a fixed-price baseline.
  Save `results/rl_policy.csv` and `results/rl_vs_fixed_margin.csv`.

## 8. Engine 5 — RNN / LSTM (notebook 06)

- Build a monthly time series of foldable review sentiment (and review volume) from the NLP
  notebook's per-review sentiment outputs aggregated by month. **Source: reviews_global.csv
  only** (reviews.csv predates foldables, so it cannot contribute to this series).
- Train an LSTM (Keras) to forecast sentiment 3 months ahead; compare with a naive
  last-value baseline (report RMSE/MAE both).
- Business output: sentiment trajectory at a hypothetical Nothing launch quarter →
  launch-timing recommendation. Save `results/sentiment_forecast.csv` + chart.
- Keep the sequence task small and defensible; honesty about limitations is graded.
  Expect a thin series: foldable reviews only exist from ~2019, giving roughly 60–80
  monthly points with a 3-month horizon — expect weak absolute accuracy and present
  the naive-baseline comparison as the primary evidence.

## 9. KPI module (src/kpi.py)

A single, documented function that consumes `results/` CSVs and prints/saves the final
business case:

- inputs: predicted price (ML/DL), segment share (ML), pain-point analysis (NLP),
  market size (enrichment), RL policy margin, unit-cost assumption.
- computes: addressable units × realistic share × (price − unit cost) per quarter;
  break-even unit volume; projected margin and cashflow over 8 quarters; margin delta of
  the RL policy vs fixed price.
- outputs `results/kpi_summary.csv` and a one-figure KPI chart (cumulative cashflow curve
  with break-even line) exported to `figures/`.
- This module is the spine of the report's "business value" section — it must run
  standalone (`python src/kpi.py`).

## 10. Report and deck (outside the agent's scope, for the group)

The agent produces notebooks, results and figures. The group writes:
- `report.pdf` — 15–20 pages: problem, role, four data sources with justification,
  methodology (engines, settings, rejected alternatives), results with interpretation of each
  visual, KPIs, limitations (no real Nothing sales data; RL in a simulated environment;
  foldable reviews are a filtered subset), AI-use statement, sources.
- `slides.pptx` — the pitch deck (already drafted).
- Zip everything as `project.zip` per the submission list.

## 11. Acceptance criteria

The build is done when:
1. `Kernel > Restart & Run All` succeeds for all six notebooks on a clean machine.
2. `results/data_verification.csv` shows all **hard** datasets pass their applicable
   thresholds (records >1,000 for core datasets; features >=25 for the specs table);
   supplementary datasets are soft warnings gated through the compiled tables. — **met
   for notebook 01 on 2026-10-29**; re-check after any dataset change.
3. Each engine has at least one saved, interpretable output CSV + one exported figure.
4. `python src/kpi.py` runs and produces the break-even and margin figures.
5. The RL notebook clearly separates simulated quantities from real-data quantities.
6. No invented data: every number traces to a dataset file or a documented, cited assumption.
7. `requirements.txt` pins every import used.

## 12. Suggested build order

1. `01_data_prep` (datasets + verification gate + `is_foldable` flag) — **done 2026-10-29**
2. `02_ml` (price regression — everything downstream depends on it)
3. `03_dl` (reuses 02's train/test setup)
4. `04_nlp` (independent of 02/03; can be built in parallel)
5. `src/kpi.py` v1 (works with ML + NLP outputs only) — **done 2026-10-29**
6. `05_rl` (needs 02's price model and 04's sentiment scores)
7. `06_rnn_lstm` (needs 04's per-review sentiment outputs)
8. Final pass: figures polish, verification, clean run of everything.
