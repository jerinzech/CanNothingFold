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

## 2. Repository structure to create

```
project/
  README.md                  # run order, dataset sources, requirements
  requirements.txt
  data/
    raw/                     # downloaded datasets, untouched
    processed/               # cleaned, joined, feature-engineered outputs
    enrichment/              # market stats, enrichment joins
  notebooks/
    01_data_prep.ipynb
    02_ml_price_segmentation.ipynb
    03_dl_neural_network.ipynb
    04_nlp_foldable_reviews.ipynb
    05_rl_pricing_agent.ipynb
    06_rnn_lstm_sentiment.ipynb
  src/
    kpi.py                   # break-even / margin model
  results/                   # all model outputs saved as CSV (graded requirement)
  figures/                   # all charts exported for report and slides
```

Rules: every notebook runs top-to-bottom on a clean machine (`Kernel > Restart & Run All`
must succeed). Every model output is saved to `results/` as CSV. Every chart is also
exported to `figures/` as PNG (300 dpi).

## 3. Data acquisition (notebook 01)

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

- Filter reviews.csv (and reviews_global.csv if needed) to foldable models using the
  `is_foldable` mapping. Print and record the corpus size honestly.
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
  notebook's per-review sentiment outputs aggregated by month.
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
2. `results/data_verification.csv` shows all core datasets pass their applicable
   thresholds (records >1,000 for all; features >=25 for specs.csv).
3. Each engine has at least one saved, interpretable output CSV + one exported figure.
4. `python src/kpi.py` runs and produces the break-even and margin figures.
5. The RL notebook clearly separates simulated quantities from real-data quantities.
6. No invented data: every number traces to a dataset file or a documented, cited assumption.
7. `requirements.txt` pins every import used.

## 12. Suggested build order

1. `01_data_prep` (datasets + verification gate + `is_foldable` flag)
2. `02_ml` (price regression — everything downstream depends on it)
3. `03_dl` (reuses 02's train/test setup)
4. `04_nlp` (independent of 02/03; can be built in parallel)
5. `src/kpi.py` v1 (works with ML + NLP outputs only)
6. `05_rl` (needs 02's price model and 04's sentiment scores)
7. `06_rnn_lstm` (needs 04's per-review sentiment outputs)
8. Final pass: figures polish, verification, clean run of everything.
