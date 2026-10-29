# CanNothingFold — Dataset Inventory and Data Dictionary

Verified inventory for the multi-country price and business analysis. This file
supersedes the earlier scan notes and corrects several entries in
`data/all-data/dataset-map.xlsx`.

- **Last verified:** 2026-10-29
- **Project root:** `/Users/jerin/Developer/CanNothingFold`
- **Raw downloads:** `data/raw/` — never edited in place; inventory and sha256 in
  `data/raw/MANIFEST.csv`
- **Cleaned outputs:** `data/processed/`
- **Compiled/enriched tables:** `data/enrichment/`
- **Analysis results:** `results/`
- **Kaggle download URL:** `https://www.kaggle.com/api/v1/datasets/download/<owner>/<slug>`

Status legend: **Core** = primary analysis source · **Supplementary** = supporting
source · **Validation** = external cross-check · **Background** = pipeline/context
only · **Manual** = hand-built or scraped enrichment · **Screened out** = inspected
and rejected · **Not downloaded** = intentionally out of scope.

---

## 1. Canonical raw inventory

The dataset IDs follow the original project map. Only the files below are copied
into `data/raw/`; the full 1.0 GB download area remains in `data/all-data/`
(untracked).

| ID | File in `data/raw/` | Shape | Status | Role / key fact |
|---|---|---|---:|---|
| D01 | `phone_information_2024.csv` | 1,715 × 31 | **Core** | UK/DE/US marketplace specs + local-currency prices; 20 Nothing listings / 5 models; 83 foldable listings / 21 models |
| D02 | `phones_2024.csv` | 1,708 × 38 | Backup | Same underlying listings as D01, USD-only price; not used |
| D03 | `mobiles_2025.csv` | 930 × 15 | Supplementary | Official launch-price comparator for PK/IN/CN/US/UAE; **0 Nothing rows**; Latin-1 |
| D04 | `gsmarena_prices.csv` | 7,127 × 23 | Validation | Global USD launch prices 2003–2024; 1 Nothing row |
| D05 | `sales_india.csv` | 3,114 × 12 | Supplementary | India-only sales/segmentation; label India-only |
| D06 | `reviews_global.csv` | 50,000 × 25 | **Core NLP** | 8 countries, 7 brands, 22 models; 4,109 foldable reviews; primary foldable corpus |
| D07 | `phone_user_review_file_1..6.csv` | 1,415,133 × 11 | Background | Masaladata reviews end May 2017; zero foldable reviews by construction; part 7 absent |
| D08 | `specs_india_2026.csv` | 4,000 × 17 | Supplementary | India 91mobiles retail scrape; 16 Nothing rows; INR |
| D09 | `specs_phonedb.csv` | 8,277 × 50 | Validation | PhoneDB specs; 3 Nothing rows; mixed-currency `Price` column |
| D10 | — | — | Not downloaded | Amazon Reviews 2023 too large; not needed |
| D11 | `spain_prices.csv` | 1,816 × 8 | Supplementary | Spain EUR retail; 9 Nothing listings / 2 models |
| D12 | `specs_india_2023.csv` | 1,020 × 11 | Screened out | India 2023; duplicate of D28; archive only |
| D13 | — | — | Not copied | PromptCloud 2019 reviews; pre-foldable background only |
| D14 | `specs_india_2026_alt.csv` | 858 × 29 | Holdout only | India 2026; 17 Nothing rows; provenance unverified, excluded from verified index |
| D15 | — | 930 × 15 | Screened out | Same shape as D03, likely a copy; do not use as a separate source |
| D16 | `archive/specs_synthetic.csv` | 15,000 × 25 | Archived | Synthetic; 43 unique models, zero foldables; **do not use** |
| D17 | — | ~833 | Screened out | Too small / single market |
| D18 | — | — | Screened out | Same issue as D17; not inspected in depth |
| D19 | — | 6,620 × 168 | Screened out | Prices in Bangladeshi taka; global price populated for only 495 rows |
| D20 | — | 4,144 × 80 | Screened out | Bangladesh mobiledokan scrape; no multi-country prices |
| D21 | — | ~20 KB | Screened out | Country coverage unverifiable |
| D22 | — | xlsx/txt | Screened out | Top-100 list only |
| D23 | — | — | Screened out | No verified multi-country prices |
| D24 | — | ~1,000,000 | Screened out | Synthetic |
| D25 | — | 33 MB | Screened out | Used-device prices, not launch/MSRP |
| D26 | — | — | Screened out | Price bands only, no model names |
| D27 | `specs_india_2025_basic.csv` | 3,260 × 20 | Supplementary | India basic retail; 11 Nothing rows; INR |
| D28 | — | 37 KB | Screened out | India-only; duplicate role covered by D12/D27/D29 |
| D29 | `specs_india_2025.csv` | 5,263 × 15 | Supplementary | India retail; 35 Nothing rows; INR |
| D30 | — | ~691K | Screened out | Synthetic, iPhone-only |
| D31 | — | — | Screened out | No verified multi-country pricing |
| D32 | `nothing_official_prices_2026-10-29.csv` | 123 × 11 | **Manual** | Official Nothing current-price snapshot, 15 markets; **not launch prices** |
| D33 | `data/enrichment/price_by_country.csv` | 19,347 × 22 | **Manual/compiled** | Main long price table |
| D34 | `data/enrichment/enrichment_market*.csv` | 3 + 18 rows | **Manual** | Global and country market seed |
| D35 | `worldbank_*.json`, `worldbank_*.csv` | 220 × 11 built | **Manual/API** | 8 World Bank indicators, 20 countries, 2015–2025 |
| D36 | `data/enrichment/foldable_prices.csv` | 271 × 22 | **Manual/compiled** | Foldable subset of D33 |

### Corrections to the original map

| Original entry | Verified correction |
|---|---|
| D01 has 16 Nothing rows | **20 Nothing listings / 5 models** (Phone (1), (2), (2a), (2a) Plus, CMF Phone 1) |
| D03 is the Nothing launch-price backbone | **D03 contains zero Nothing models.** It is a competitor/price-level comparator. Nothing launch prices are hand-collected in D32/manual anchors |
| D08 "unknown, page did not render" | **4,000 × 17**, 16 Nothing rows, INR retail; usable as an India supplement |
| D09 "8k+ rows, 40+ features" | **8,277 × 50**, but the `Price` column mixes currencies; use only for spec cross-checks |
| D11 "unknown" | **1,816 × 8**, 9 Nothing listings / 2 models, Spain EUR retail |
| D14 "Kaggle page not found" | File is present: **858 × 29**, 17 Nothing rows, but provenance is unverified → holdout only |
| D27 "screened out, India-only" | **Promoted to India supplement**: 3,260 × 20, 11 Nothing rows; one obvious 2,599 INR typo dropped as an outlier |
| D29 "~500 rows, too small" | **5,263 × 15**, 35 Nothing rows; usable India supplement |
| D07 "7 files, ~1.4M" | **6 files present, 1,415,133 rows**; part 7 absent; ends May 2017 |
| D15 "reference" | Same 930 × 15 shape as D03; likely a copy — drop as a separate source |
| D21 "country coverage unverifiable" | Not a D03 duplicate; it is a separate ~20 KB trend file and remains screened out |
| D32 target >1,000 hand-collected rows | 24 cited launch anchors + 123 current-price rows; the >1,000-row gate is applied to compiled D33 instead |
| D35 "World Bank 2024 CSV" | Original D35 part 1 is malformed (multi-line metadata); replaced by API JSON for **8 indicators × 20 countries × 2015–2025** |

---

## 2. Core and supplementary datasets

### 2.1 D01 — `phone_information_2024.csv` (core)

| Field | Value |
|---|---|
| Source | https://www.kaggle.com/datasets/willianoliveiragibin/phone-information-2024 |
| Shape | **1,715 rows × 31 columns** |
| Coverage | UK, Germany, US; years 2017–2024 |
| Stores | Amazon DE 585, Amazon UK 488, Amazon US 455, AliExpress 97, Best Buy 48, Samsung 33, Motorola 7, OnePlus 2 |
| Nothing | **20 listings / 5 models** |
| Foldables | **83 listings / 21 models** |
| Prices | `price` is **local currency**; `currency` is USD/EUR/GBP; `price_USD` is the dataset's own conversion |
| Gate | **Passes both**: 1,715 > 1,000; 31 features ≥ 25 |

**Use:** core specs + marketplace price source. Only Amazon UK/DE/US map cleanly to
countries. Aggregate multiple listings to the **median per model × country** before
computing country ratios. `price` must not be treated as USD: filter on `currency`
or use `price_USD` for cross-country comparisons.

**Quirks verified:**
- Marketplace prices, not MSRP; the same model/store can have several listings.
- AliExpress/Best Buy/Samsung/Motorola/OnePlus rows have no country-bearing store;
  exclude them from country tables.
- Foldable ratios rest on only 21 models / 83 listings, so they are directional.

### 2.2 D02 — `phones_2024.csv` (backup)

1,708 × 38; same store/year mix; `price_usd` only, no local currency; 83 foldable
listings and 20 Nothing rows. Kept as a feature cross-check, not used in the compiled
price tables.

### 2.3 D03 — `mobiles_2025.csv` (launch comparator, not Nothing)

| Field | Value |
|---|---|
| Source | https://www.kaggle.com/datasets/abdulmalik1518/mobiles-dataset-2025 |
| Shape | **930 rows × 15 columns** |
| Countries | Pakistan, India, China, USA, UAE/Dubai |
| Years | 2014–2025 (292 rows from 2024, only 12 from 2025) |
| Foldables | **22 rows** |
| Nothing models | **0** |
| Encoding | **Latin-1** |
| Gate | Fails the >1,000-row rule → supplementary; apply the gate to D33 instead |

**Use:** competitor launch-price comparator and market price-level index for five
countries. It is **not** a Nothing source.

**Quirks verified:**
- Prices are currency-prefixed strings (`"PKR 224,999"`, `"INR 79,999"`, `"USD 799"`,
  `"AED 2,799"`); one Pakistan value is `"Not available"`.
- Several values use a **decimal comma**, e.g. `"USD 396,22"`. Parsing must treat a
  single comma followed by two digits as a decimal separator, not a thousands
  separator.
- Company naming is inconsistent (`Poco` vs `POCO`).
- Year distribution is skewed to 2023–2024; do not treat it as a balanced panel.

### 2.4 D04 — `gsmarena_prices.csv` (validation)

7,127 × 23; global USD launch prices 2003–2024; 92 brands; 1 Nothing row
(Phone (2a) Plus, 2024, $399.60); 48 regex foldable matches, of which ~20 are from
2019+ before excluding feature phones. `Price in USD` is populated for all rows,
which is suspiciously complete — validate against known MSRPs before trusting.
Not used as a country-price source.

### 2.5 D05 — `sales_india.csv` (India segmentation)

3,114 × 12; India only; INR; columns include brand, model, memory/storage, ratings,
selling price, original price and discount. Use for notebook 02 segmentation and label
all outputs India-only.

### 2.6 D06 — `reviews_global.csv` (primary foldable NLP corpus)

50,000 × 25; 8 countries (USA 6,435; Brazil 6,419; UAE 6,261; Australia 6,219;
UK 6,210; Canada 6,170; Germany 6,162; India 6,124); 7 brands; 22 models;
**4,109 foldable rows** (Razr 40 2,395; Galaxy Z Flip 1,714); review dates
2022-10-22 to 2025-10-21.

**Quirk:** only **110 unique review texts** across 50,000 rows — the corpus is
synthetic/repetitive. Use it for pipeline demonstration and country aggregates, never
for claims about real consumer sentiment. `price_local` is a formatted string and some
per-row prices (e.g. Razr 40 India) are implausible; use medians only.

### 2.7 D07 — `phone_user_review_file_1..6.csv` (background)

Six parts, **1,415,133 rows × 11 columns** total; Latin-1; latest review May 2017.
Part 7 is not present. The corpus cannot contain foldable reviews (first foldable
shipped 2019); it exists only for the record-count gate and background sentiment.
Notebook 01 reduces it to essential columns and saves a small/cleaned background table.

### 2.8 D08 / D27 / D29 — India retail supplements

| Dataset | Shape | Nothing rows | Character |
|---|---:|---:|---|
| D08 `specs_india_2026.csv` | 4,000 × 17 | 16 | 91mobiles retail scrape, 2008–2026; INR |
| D27 `specs_india_2025_basic.csv` | 3,260 × 20 | 11 | Basic India retail; INR; brand column often `Other` |
| D29 `specs_india_2025.csv` | 5,263 × 15 | 35 | India retail; INR; includes many brands |

These are **retail/discounted prices**, not launch MSRPs. Model strings include storage
and RAM variants; the compiler normalises them to a `model_key` and aggregates to
medians. D27 contains one obvious typo (`nothing phone 2a plus 12gb ram` at 2,599 INR,
roughly 10× too low); rows below 30% of the same-source/model median are dropped
before aggregation.

### 2.9 D09 — `specs_phonedb.csv` (validation)

8,277 × 50; 3 Nothing Phone (1) rows. The `Price` column mixes currencies
(69,800 for one row, 499/399 for others), so it is not used in the compiled price
tables. Useful only for spec cross-checks.

### 2.10 D11 — `spain_prices.csv` (Spain retail)

1,816 × 8; 37 brands; 9 Nothing listings / 2 models (Phone (1), Phone (2)); EUR;
`Final Price` is numeric with no missing values. This is a retail snapshot, not a
launch price.

### 2.11 D12 / D28 — India 2023 duplicate (archived)

D12 is 1,020 × 11 with 5 Nothing rows; D28 is a 37 KB India-only file. They cover the
same role and are not used. Keep D12 in `data/raw/` only for provenance.

### 2.12 D14 — India 2026 holdout (unverified)

858 × 29; 17 Nothing rows; INR; includes contradictory Phone (3) prices (54,999 vs
79,999 INR) and an unverified Kaggle provenance. Use only as a holdout/unverified
sensitivity check; it is excluded from the verified country index and the collection
template.

---

## 3. Manual and compiled enrichment

### 3.1 `nothing_official_current.csv` (D32)

- **123 rows × 11 columns**, collected **2026-10-29** from 15 Nothing storefronts:
  UK, US, DE, FR, ES, IT, JP, AU, NL, AT, BE, PT, IE, FI, MX.
- Fields: `store_host`, `country`, `currency`, `model`, `price_local`,
  `price_local_max_variant`, `variants_seen`, `price_type`, `source`, `source_url`,
  `collected_at`.
- These are **current listed prices**, not launch prices. Do not mix them with
  `official_launch` in a ratio.
- Coverage is uneven: 9 models in most EU stores, 5 in the UK, **2 in the US**
  (Phone (3), Phone (4a) Pro). India and UAE storefronts load but expose no visible
  collection prices, so they have no rows here.
- Raw snapshot: `data/raw/nothing_official_prices_2026-10-29.csv`.

### 3.2 `nothing_launch_prices_manual.csv` (D32 companion)

- **24 rows × 8 columns**; 8 models: Phone (1), (2), (2a), (2a) Plus, CMF Phone 1,
  Phone (3), (3a), (3a) Pro.
- Markets: India (8), UK (6), US (6), Germany (4). No UAE/Japan/Spain/France anchors
  yet.
- Fields: `model`, `country`, `currency`, `local_price`, `source`, `source_url`,
  `collected_at`, `notes`.
- Every row has a cited source URL; these are the only true Nothing launch prices in
  the repo.

### 3.3 `nothing_prices.csv`

- **182 rows × 22 columns**; 13 Nothing models.
- Combines D01 marketplace, D08/D11/D27/D29 retail, D14 unverified retail, the D32
  official current snapshot and the 24 manual launch anchors.
- `price_type` values: `official_launch`, `official_current`, `retail`,
  `retail_unverified`, `marketplace`.
- Model keys are storage/RAM-normalised; `model_id` is a URL-safe key.
- Do not compare across `price_type` without grouping by it. In particular,
  `official_current` is a 2026 snapshot while `official_launch` is the original MSRP.

### 3.4 `nothing_prices_template.csv`

- **104 rows = 13 models × 8 target countries** (India, UK, Germany, US, UAE, Japan,
  Spain, France).
- Status counts: **24 `have`** (official launch), **50 `have_current`** (current or
  retail only), **30 `need`**.
- `need` is concentrated in UAE (13), US (4), Japan (4), France (4), Spain (2), UK (2),
  India (1). This is the collection worklist; each row says
  `Collect official launch price with source URL.`
- A model × country marked `have_current` still lacks its original launch price.

### 3.5 `price_by_country.csv` (D33)

- **19,347 rows × 22 columns.**
- One row per source × country × model string × price type, after aggregating
  listings/variants to medians. Multiple storage variants can remain as separate rows;
  use `model_key` or `model_id` for model-level joins.
- Schema:

```text
model_id, brand, model, release_year, is_foldable, country, currency,
local_price, price_usd, price_eur, price_type, source, source_url, collected_at,
n_listings, local_price_min, local_price_max, us_price_usd, ratio_vs_us,
verified, source_status, model_key
```

- `price_type` semantics:

| `price_type` | Source | Meaning |
|---|---|---|
| `official_launch` | D03 + manual | Original launch/MSRP; D03 rows are competitors, manual rows are Nothing |
| `official_current` | D32 | Current official store price on 2026-10-29 |
| `marketplace` | D01 | Amazon/brand-store listing, median per model × country |
| `retail` | D08, D11, D27, D29 | Retail/discounted price snapshot |
| `retail_unverified` | D14 | Unverified holdout; exclude from verified outputs |

- `verified=False` only for D14 (`source_status="unverified"`); all other compiled
  sources are verified.
- `ratio_vs_us` is a within-model ratio. D03 rows use the **same storage variant's**
  US price; other sources use a model-level US median/fallback. Do not compute
  cross-model medians without grouping by `price_type` and segment.

### 3.6 `foldable_prices.csv` (D36)

271 rows × 22 columns; the `is_foldable=True` subset of D33. Ready for notebooks 02–04.
Includes D01 foldable marketplace rows, D03 foldable comparators, India retail
foldables and the two Spain D11 foldables. The Nothing launch/current rows are not
foldable (Nothing has no foldable product), so foldable Nothing prices do not exist.

### 3.7 World Bank enrichment

- `enrichment_wb.csv`: **220 rows × 11 columns** = 20 countries × 11 years
  (2015–2025).
- `enrichment_wb_latest.csv`: 20 rows, latest non-null year per country.
- Indicators: `mobile_subscriptions_per_100`, `internet_users_pct`,
  `fixed_broadband_per_100`, `gdp_per_capita_usd`, `gdp_current_usd`, `population`,
  `urban_population_pct`, `unemployment_pct`.
- Raw cached JSON: `data/raw/worldbank_*.json` (8 indicator files plus a combined
  response). The original D35 part-1 CSV is malformed and is retained only for
  provenance.
- Join on `country` for the cleaned reviews table; use
  `mobile_subscriptions_per_100` explicitly, not “first non-country column”.

### 3.8 Market enrichment

- `enrichment_market.csv`: 3 rows (2023–2025) with global smartphone shipments,
  foldable shipments and derived foldable share. 2025: 1,250M smartphones, 20.6M
  foldables, 1.65% share; Nothing 3.0M units, +86% YoY (Omdia).
- `enrichment_market_country.csv`: 18 rows with `status` in
  {`verified` 7, `secondary` 3, `derived` 1, `to_fill` 7}. India foldable shipments,
  Nothing India share and 2025 shipments for UK/DE/UAE/ES/FR remain `to_fill`.
  These are seeds, not a complete country panel.

### 3.9 Fixed FX assumptions

All compiled tables use a fixed EUR-per-unit table (`FX_ASOF = 2026-10-29`):

| Currency | EUR per 1 unit | Note |
|---|---:|---|
| EUR | 1.0000 | base |
| USD | 0.9200 | documented assumption; 2026-10-29 market cross-check ≈0.898 |
| GBP | 1.1700 | |
| INR | 0.0104 | |
| PKR | 0.0032 | |
| CNY | 0.1280 | |
| AED | 0.2500 | |
| JPY | 0.0060 | |
| AUD | 0.6300 | |
| MXN | 0.0480 | |
| CAD | 0.6800 | |

`price_usd = local_price × EUR_PER_UNIT[currency] / 0.92`. The table is intentionally
fixed for reproducibility; do not silently update one currency. Re-run
`src/build_enrichment.py` after any FX change.

---

## 4. Verification gate

Notebook 01 applies the graded gate. Rules: **records > 1,000** for core datasets;
**features ≥ 25** for the core specs table only.

| Dataset | Rows | Features | Gate | Treatment |
|---|---:|---:|---|---|
| D01 `phone_information_2024.csv` | 1,715 | 31 | **Passes both** | Core |
| D02 `phones_2024.csv` | 1,708 | 38 | Passes both | Backup |
| D03 `mobiles_2025.csv` | 930 | 15 | Fails row gate | Supplementary; gate D33 instead |
| D04 `gsmarena_prices.csv` | 7,127 | 23 | Passes rows; 23 features | Validation only |
| D05 `sales_india.csv` | 3,114 | 12 | Passes rows | India-only |
| D06 `reviews_global.csv` | 50,000 | 25 | **Passes both** | NLP core |
| D07 background (6 parts) | 1,415,133 | 11 | Passes rows | Background only |
| D08 India 2026 | 4,000 | 17 | Passes rows | India supplement |
| D11 Spain | 1,816 | 8 | Passes rows | Spain supplement |
| D27 India basic | 3,260 | 20 | Passes rows | India supplement |
| D29 India 2025 | 5,263 | 15 | Passes rows | India supplement |
| D33 `price_by_country.csv` | 19,347 | 22 | **Passes both** | Compiled price table |
| `nothing_prices.csv` | 182 | 22 | Manual supplement; soft | Not a row-gate dataset |
| `enrichment_wb.csv` | 220 country-years | 11 | Country-year table | Not a row-gate dataset |

The synthetic `specs.csv` is archived; notebook 01 must load D01 explicitly rather
than searching for `specs*.csv` (the old non-recursive `RAW.glob("*.csv")` approach
could silently pick the synthetic file).

---

## 5. Preliminary country price indices

All ratios are within-model versus the US price after the fixed FX conversion.
**Directional only** — small samples, marketplace/retail snapshots and mixed price
types. `results/country_price_index.csv` groups by `segment` and `price_type` so
launch, retail, marketplace and current prices are never mixed.

### 5.1 D03 competitor launch prices (not Nothing)

| Market | All models | n | Foldables | n |
|---|---:|---:|---:|---:|
| India | **0.943×** | 897 | **0.968×** | 17 |
| China | **0.919×** | 897 | **0.940×** | 17 |
| UAE | **1.011×** | 897 | **1.006×** | 17 |
| Pakistan | **0.698×** | 896 | **0.785×** | 17 |
| US | 1.000× | 897 | 1.000× | 17 |

The old preliminary India figure of 1.006× is **superseded**: it came from a
model-key match that ignored storage variants and from a decimal-comma parsing bug.
The current figure is 0.943× for all competitor models and 0.968× for foldables.

### 5.2 D01 marketplace prices

| Market | All models | n | Foldables | n |
|---|---:|---:|---:|---:|
| UK | **1.087×** | 283 | **1.118×** | 16 |
| Germany | **1.005×** | 314 | **1.143×** | 17 |
| US | 1.000× | 307 | 1.000× | 12 |

### 5.3 Nothing official current prices (2026-10-29)

| Market | Median ratio | n models | Read |
|---|---:|---:|---|
| United Kingdom | **1.297×** | 5 | GBP list premium plus FX |
| Germany | **1.197×** | 9 | EUR list premium |
| Spain | **1.197×** | 9 | same EUR list as Germany |
| France | **1.258×** | 9 | higher EUR list |
| Japan | **1.104×** | 9 | modest premium |
| Australia | **1.390×** | 9 | AUD list premium |
| Mexico | **1.116×** | 8 | mixed by model |
| US | 1.000× | 2 | reference |

Only Phone (3) and Phone (4a) Pro exist in both the US and the other stores, so the
two-model ratios are the cleanest launch-like comparisons: Phone (3) is 1.24× in
Germany, 1.27× in the UK and 1.16× in Japan; Phone (4a) Pro is 1.15×, 1.32× and
1.04× respectively.

### 5.4 Nothing retail snapshots

| Source | Market | Median ratio | n rows / models | Caveat |
|---|---|---:|---:|---|
| D01 marketplace | Germany | 0.950× | 5 / 5 | old Phone (1)/(2)/(2a) listings |
| D01 marketplace | UK | 1.080× | 5 / 5 | same |
| D08 91mobiles | India | 0.841× | 17 / 9 | discounted retail |
| D29 India 2025 | India | 0.735× | 13 / 5 | discounted retail |
| D27 India basic | India | 0.720× | 12 / 5 | discounted retail |
| D11 Spain | Spain | 1.344× | 2 / 2 | Phone (1)/(2) only |
| D14 India 2026 | India | 1.042× | 17 / 8 | **unverified; do not publish** |

India retail prices are consistently below US launch prices after FX; this is a
discount/street-price effect, not evidence that Nothing’s India MSRP was lower. Use
the manual `official_launch` anchors for MSRP comparisons.

**Interpretation for the business case:** UK/Germany/EU carry a VAT-driven premium
over the US; Japan is close to parity; India street prices are discounted but the
launch MSRP is near US parity. Foldable comparators carry a larger premium in
UK/Germany than all-model averages. Validate all of this against
`nothing_prices_template.csv` before publishing.

---

## 6. Known gaps and collection worklist

1. **Nothing launch prices are incomplete.** 30 of 104 model × country cells are
   `need`; UAE alone accounts for 13. No manual launch anchors exist for UAE, Japan,
   Spain or France.
2. **Official current snapshot is uneven.** The US store exposes only Phone (3) and
   Phone (4a) Pro; India/UAE expose no collection prices; UK exposes 5 models vs 9 in
   the EU.
3. **No Nothing sales by country.** D05 is India-only. Nothing’s 3.0M global shipments
   and +86% growth are from Omdia; country shares are paywalled.
4. **Country market panel is incomplete.** India foldable shipments, Nothing India
   share and 2025 shipments for UK/DE/UAE/ES/FR are `to_fill` in
   `enrichment_market_country.csv`.
5. **D14 is not verified.** Do not use it in the main index; keep it as a holdout.
6. **D07 ends May 2017** and has no foldables; D06 is the only foldable review corpus
   (and is synthetic-like, 110 unique texts).
7. **D10/D13/D15–D26/D28/D30/D31** are not part of the analysis; do not add them to
   the core pipeline without a new verification pass.
8. **D03 has no Nothing models.** Any “Nothing launch price” must come from the manual
   anchors, the official store snapshot (current, not launch) or a new collection.

The collection template is `data/enrichment/nothing_prices_template.csv`; fill a
`need` row only with a source URL and a date, then re-run `src/build_enrichment.py`.

---

## 7. Reproduce

```bash
# 1. Refresh the official Nothing snapshot (network; optional if raw snapshot exists)
.venv/bin/python src/collect_nothing_prices.py

# 2. Refresh/rebuild World Bank tables (uses cached raw JSON when present)
.venv/bin/python src/fetch_worldbank.py

# 3. Rebuild all compiled/enrichment tables and the country index
.venv/bin/python src/build_enrichment.py

# 4. Rebuild the raw-file manifest (sha256, rows, columns)
.venv/bin/python src/build_manifest.py

# 5. Run notebook 01 top-to-bottom
.venv/bin/python -m jupyter nbconvert --to notebook --execute \
  notebooks/01_data_prep.ipynb --inplace
```

Deterministic outputs:

- `data/enrichment/price_by_country.csv` — 19,347 × 22
- `data/enrichment/foldable_prices.csv` — 271 × 22
- `data/enrichment/nothing_prices.csv` — 182 × 22
- `data/enrichment/nothing_prices_template.csv` — 104 × 10
- `data/enrichment/enrichment_wb.csv` — 220 × 11
- `data/enrichment/enrichment_wb_latest.csv` — 20 × 11
- `data/enrichment/enrichment_market.csv` — 3 × 8
- `data/enrichment/enrichment_market_country.csv` — 18 × 9
- `results/country_price_index.csv` — 35 rows

---

## 8. Repository layout

```text
CanNothingFold/
  data/
    raw/                         # untouched downloads + MANIFEST.csv (gitignored)
      archive/specs_synthetic.csv
      nothing_official_prices_2026-10-29.csv
      worldbank_*.json
    processed/                   # notebook 01 cleaned outputs (gitignored)
      phone_models_clean.csv
      mobiles_clean.csv
      sales_india_clean.csv
      reviews_global_clean.csv
      reviews_background_clean.csv
      spain_prices_clean.csv
      price_by_country_clean.csv
      nothing_prices_clean.csv
      foldable_prices_clean.csv
    enrichment/                  # compiled tables (tracked)
      price_by_country.csv
      foldable_prices.csv
      nothing_prices.csv
      nothing_prices_template.csv
      nothing_official_current.csv
      nothing_launch_prices_manual.csv
      enrichment_wb.csv
      enrichment_wb_latest.csv
      enrichment_market.csv
      enrichment_market_country.csv
  results/
    country_price_index.csv
    data_verification.csv
    data_quality_summary.csv
    data_missingness.csv
  src/
    collect_nothing_prices.py
    fetch_worldbank.py
    build_enrichment.py
    build_manifest.py
```

---

## 9. Source links

- D01: https://www.kaggle.com/datasets/willianoliveiragibin/phone-information-2024
- D02: https://www.kaggle.com/datasets/jakubkhalponiak/phones-2024
- D03: https://www.kaggle.com/datasets/abdulmalik1518/mobiles-dataset-2025
- D04: https://www.kaggle.com/datasets/beridzeg45/gsmarena-smartphones
- D05: https://www.kaggle.com/datasets/yaminh/smartphone-sale-dataset
- D06: https://www.kaggle.com/datasets/mohankrishnathalla/mobile-reviews-sentiment-and-specification
- D07: https://www.kaggle.com/datasets/masaladata/14-million-cell-phone-reviews
- D08: https://www.kaggle.com/datasets/suresh2837/mobile-phones-specs-and-prices-dataset-20082026
- D09: https://www.kaggle.com/datasets/sady36/mobile-phones-specs
- D11: https://www.kaggle.com/datasets/juanmerinobermejo/smartphones-price-dataset
- D27: https://www.kaggle.com/datasets/rohsanyadav/smartphones-dataset
- D29: https://www.kaggle.com/datasets/vashisthrahul13/mobile-price-and-specs-2025
- World Bank: https://data.worldbank.org/
- Nothing stores: https://nothing.tech/ (and country subdomains)
