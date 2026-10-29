# Enrichment tables

Compiled by `src/build_enrichment.py`; World Bank tables by `src/fetch_worldbank.py`.
Full provenance and caveats: [`../datasets.md`](../datasets.md).

| File | Rows | Grain |
|---|---:|---|
| `price_by_country.csv` | 19,347 | source × country × model string × price type |
| `foldable_prices.csv` | 271 | `is_foldable=True` subset of the above |
| `nothing_prices.csv` | 182 | Nothing-only, all price types |
| `nothing_prices_template.csv` | 104 | 13 models × 8 target countries |
| `nothing_official_current.csv` | 123 | official store, country × model, 2026-10-29 |
| `nothing_launch_prices_manual.csv` | 24 | cited launch anchors, 8 models / 4 markets |
| `enrichment_wb.csv` | 220 | country × year, 2015–2025 |
| `enrichment_wb_latest.csv` | 20 | latest non-null year per country |
| `enrichment_market.csv` | 3 | global year, 2023–2025 |
| `enrichment_market_country.csv` | 18 | country × metric seed |

## Key columns

`price_by_country.csv` and its subsets:

```text
model_id, brand, model, release_year, is_foldable, country, currency,
local_price, price_usd, price_eur, price_type, source, source_url, collected_at,
n_listings, local_price_min, local_price_max, us_price_usd, ratio_vs_us,
verified, source_status, model_key
```

- `model_key` strips storage/RAM and normalises parentheses, so `Phone (2a)` →
  `phone 2a` and `Phone (2a) Plus` → `phone 2a plus`.
- Multiple storage variants may remain as separate rows with the same `model_key`.
- `ratio_vs_us` is a within-model ratio. D03 uses the same storage variant's US price;
  other sources use a model-level US median/fallback.
- `verified=False` marks D14 holdout rows only.

## Price types — do not mix

| Type | Meaning |
|---|---|
| `official_launch` | Original MSRP; D03 = competitors, manual = Nothing |
| `official_current` | Current Nothing store price, 2026-10-29 |
| `marketplace` | D01 Amazon/brand-store listings |
| `retail` | D08/D11/D27/D29 discounted retail |
| `retail_unverified` | D14 holdout; excluded from verified outputs |

## FX assumption

Fixed EUR-per-unit rates (`FX_ASOF = 2026-10-29`):
EUR 1.0, USD 0.92, GBP 1.17, INR 0.0104, PKR 0.0032, CNY 0.128, AED 0.250,
JPY 0.0060, AUD 0.63, MXN 0.048, CAD 0.68.

`price_usd = local_price × rate / 0.92`. The table is intentionally fixed for
reproducibility; change rates only with a documented rerun.

## Status

- D03 has **zero Nothing models** — it is a competitor comparator.
- Nothing launch prices are only the 24 cited rows in
  `nothing_launch_prices_manual.csv`.
- `nothing_prices_template.csv` has 24 `have`, 50 `have_current`, 30 `need`.
- India/UAE official stores expose no collection prices; the US store exposes only
  Phone (3) and Phone (4a) Pro.
- `enrichment_market_country.csv` still has 7 `to_fill` metrics; do not present the
  country market panel as complete.
