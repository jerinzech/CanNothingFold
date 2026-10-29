# Handoff guide — running CanNothingFold on a new machine

This is everything a teammate needs to reproduce the project end-to-end.

## 0. What comes from where

| Piece | Size | How the teammate gets it |
|---|---|---|
| Code, notebooks, `src/`, `report.md`, docs | ~10 MB | `git clone` from GitHub |
| `data/enrichment/` (compiled price/market/WB tables) | 5.3 MB | in the repo (tracked) |
| `results/` (model output CSVs), `figures/` (PNGs) | ~5 MB | in the repo (tracked) |
| **`data/raw/` (all datasets + MANIFEST + caches)** | 490 MB (zip: ~134 MB) | **shared zip — not on GitHub** |
| `data/processed/` (cleaned outputs) | 84 MB | **regenerates itself** by running notebook 01 |
| `.venv/` | ~2 GB | **regenerates itself** from `requirements.txt` |

`data/raw/` is gitignored on purpose (large downloads). It is **not** regenerable
without re-downloading ~8 Kaggle datasets, the World Bank API and the Nothing
store snapshot — so share the zip once (Google Drive / Dropbox / university
share), and verify it with the MANIFEST checksums (step 3 below).

## 1. Clone and set up the environment

Tested on **Python 3.9** (macOS, arm64). All package versions are pinned.

```bash
git clone https://github.com/jerinzech/CanNothingFold.git
cd CanNothingFold
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Unpack the shared data

Unzip the shared `data_raw.zip` **from the repo root** so the contents land in
`data/raw/` (it must contain `MANIFEST.csv`, the CSVs, the `worldbank_*.json`
caches, `nothing_official_prices_2026-10-29.csv` and `archive/`):

```bash
unzip /path/to/data_raw.zip       # creates data/raw/...
ls data/raw/MANIFEST.csv          # sanity check
```

## 3. Verify the data (integrity check)

`data/raw/MANIFEST.csv` ships with the zip and carries a sha256 per file:

```bash
python - <<'EOF'
import hashlib, pandas as pd
m = pd.read_csv("data/raw/MANIFEST.csv")
bad = [r.file for _, r in m.iterrows()
       if hashlib.sha256(open(f"data/raw/{r.file}", "rb").read()).hexdigest() != r.sha256]
print("data OK" if not bad else f"CORRUPT: {bad}")
EOF
```

If any file fails, re-download the zip — do not proceed with corrupt data.

## 4. Run the pipeline (full chain, in order)

```bash
# optional sanity: rebuild the compiled tables and confirm nothing drifts
python src/build_enrichment.py        # rewrites data/enrichment/* from data/raw
python src/build_manifest.py          # rewrites data/raw/MANIFEST.csv

# notebooks, in order (each runs top-to-bottom from a fresh kernel):
for nb in notebooks/0*.ipynb; do
  python -m jupyter nbconvert --to notebook --execute "$nb" --inplace
done

python src/kpi.py                     # prints the final business case
```

Notes:
- Notebook 01 rebuilds everything in `data/processed/` and the verification
  gate outputs in `results/`. Notebooks 02–06 rebuild the model outputs and
  figures. Nothing needs a network connection: the World Bank JSON caches and
  the Nothing store snapshot (2026-10-29) ship inside `data/raw/`.
- `src/collect_nothing_prices.py` and `src/fetch_worldbank.py` are only needed
  to refresh those snapshots — the pipeline does not require them.
- TensorFlow training is not bit-for-bit deterministic, so notebook 03's
  neural-network metrics may differ by ~0.01 R² from the committed run; all
  other engines are seeded (`random_state=42`) and reproduce exactly.
- Total runtime: ~5 minutes on a modern laptop.

## 5. If you'd rather re-download than use the zip

Every file's source is documented in `data/datasets.md` (and per-file in
`data/raw/MANIFEST.csv`): 8+ Kaggle datasets (needs a free Kaggle account,
files must be renamed to the canonical names in MANIFEST), the World Bank API
(`src/fetch_worldbank.py`), and the Nothing official stores
(`src/collect_nothing_prices.py`). The zip is strongly recommended — it is
faster and checksum-verified.

## 6. Expected final state

After the full chain:

- 9 files in `data/processed/*_clean.csv`
- 19 CSVs in `results/` (verification gate, model outputs, KPI summary/cashflow)
- 13 PNGs in `figures/` (300 dpi)
- `python src/kpi.py` prints the business case ending in:
  `recommendation: GO (5/5 checks)` — see `report.md` for the full story.

## 7. Maintainer note (do not push data/all-data)

`data/all-data/` is a 1 GB archive of the *original* downloads kept for
provenance. It duplicates `data/raw/` under different names, is not used by
any notebook or script, and GitHub rejects files over 100 MB anyway. Keep it
out of git history; `data/raw/` + `MANIFEST.csv` is the canonical copy.
