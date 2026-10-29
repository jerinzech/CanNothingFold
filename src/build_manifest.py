"""Rebuild data/raw/MANIFEST.csv from the current raw files.

The manifest is a provenance inventory: file name, size, row/column counts where
parseable, sha256, dataset ID, source and a short note.  It intentionally scans
only data/raw/ (plus data/raw/archive/) and never modifies the raw files.

Run:  .venv/bin/python src/build_manifest.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

META: dict[str, tuple[str, str, str]] = {
    "phone_information_2024.csv": (
        "D01", "kaggle: willianoliveiragibin/phone-information-2024",
        "core specs + UK/DE/US marketplace prices; local currency in price",
    ),
    "phones_2024.csv": (
        "D02", "kaggle: jakubkhalponiak/phones-2024",
        "backup core specs; USD-only price",
    ),
    "mobiles_2025.csv": (
        "D03", "kaggle: abdulmalik1518/mobiles-dataset-2025",
        "5-country launch comparator; Latin-1; no Nothing rows",
    ),
    "gsmarena_prices.csv": (
        "D04", "kaggle: beridzeg45/gsmarena-smartphones",
        "global USD launch validation; 1 Nothing row",
    ),
    "sales_india.csv": (
        "D05", "kaggle: yaminh/smartphone-sale-dataset",
        "India-only sales/segmentation",
    ),
    "reviews_global.csv": (
        "D06", "kaggle: mohankrishnathalla/mobile-reviews-sentiment-and-specification",
        "8-country reviews; primary foldable NLP corpus",
    ),
    "specs_india_2026.csv": (
        "D08", "kaggle: suresh2837/mobile-phones-specs-and-prices-dataset-20082026",
        "India 91mobiles retail supplement; INR",
    ),
    "specs_phonedb.csv": (
        "D09", "kaggle: sady36/mobile-phones-specs",
        "PhoneDB specs cross-check; mixed-currency price column",
    ),
    "spain_prices.csv": (
        "D11", "kaggle: juanmerinobermejo/smartphones-price-dataset",
        "Spain EUR retail; 9 Nothing listings / 2 models",
    ),
    "specs_india_2023.csv": (
        "D12", "kaggle: harshwardhanpj/smartphones",
        "India 2023; duplicate of D28; archive only",
    ),
    "specs_synthetic.csv": (
        "D16", "kaggle: shraddha4ever20/smartphone-specifications-dataset",
        "synthetic specs; 43 models, zero foldables; archived, do not use",
    ),
    "specs_india_2026_alt.csv": (
        "D14", "kaggle: abhishekmondal/indian-smartphones-dataset-2026 (provenance unverified)",
        "India 2026 holdout; excluded from verified index",
    ),
    "specs_india_2025_basic.csv": (
        "D27", "kaggle: rohsanyadav/smartphones-dataset",
        "India basic retail supplement; INR",
    ),
    "specs_india_2025.csv": (
        "D29", "kaggle: vashisthrahul13/mobile-price-and-specs-2025",
        "India retail supplement; INR",
    ),
    "worldbank_mobile_subscriptions.csv": (
        "D35p1", "World Bank DataBank",
        "original mobile-subscription CSV; malformed multi-line metadata, superseded by API JSON",
    ),
    "worldbank_country_meta.csv": (
        "D35p2", "World Bank DataBank",
        "country/region/income metadata",
    ),
    "worldbank_indicator_meta.csv": (
        "D35p3", "World Bank DataBank",
        "indicator metadata",
    ),
    "nothing_official_prices_2026-10-29.csv": (
        "D32", "Nothing official stores",
        "official current-price snapshot; 15 markets; not launch prices",
    ),
    "worldbank_indicators_2026-10-29.json": (
        "D35", "World Bank API",
        "combined cached JSON for 8 indicators, 20 countries, 2015-2025",
    ),
}

for part in range(1, 7):
    META[f"phone_user_review_file_{part}.csv"] = (
        f"D07p{part}", "kaggle: masaladata/14-million-cell-phone-reviews",
        f"background review corpus part {part}; Latin-1; ends May 2017",
    )

for code in (
    "IT.CEL.SETS.P2", "IT.NET.BBND.P2", "IT.NET.USER.ZS", "NY.GDP.MKTP.CD",
    "NY.GDP.PCAP.CD", "SL.UEM.TOTL.ZS", "SP.POP.TOTL", "SP.URB.TOTL.IN.ZS",
):
    META[f"worldbank_{code}.json"] = (
        "D35", "World Bank API",
        f"cached raw response for indicator {code}",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def count_rows(path: Path) -> int | str:
    try:
        rows = 0
        for chunk in pd.read_csv(
            path, chunksize=500_000, encoding="latin-1", low_memory=False, usecols=[0]
        ):
            rows += len(chunk)
        return rows
    except Exception:
        try:
            return sum(1 for _ in path.open("rb")) - 1
        except Exception:
            return ""


def count_columns(path: Path) -> int | str:
    try:
        return len(pd.read_csv(path, nrows=5, encoding="latin-1", low_memory=False).columns)
    except Exception:
        return ""


def main() -> None:
    paths = sorted(RAW.glob("*.csv")) + sorted((RAW / "archive").glob("*.csv"))
    paths += sorted(RAW.glob("*.json"))
    rows = []
    for path in paths:
        if path.name == "MANIFEST.csv" or path.name.startswith("."):
            continue
        rel = path.relative_to(RAW).as_posix()
        dataset_id, source, note = META.get(path.name, ("", "", ""))
        if path.suffix == ".csv":
            n_rows, n_cols = count_rows(path), count_columns(path)
        else:
            n_rows, n_cols = "", ""
        rows.append({
            "file": rel,
            "bytes": path.stat().st_size,
            "rows": n_rows,
            "cols": n_cols,
            "sha256": sha256(path),
            "dataset_id": dataset_id,
            "source": source,
            "notes": note,
        })
    manifest = pd.DataFrame(rows)
    manifest.to_csv(RAW / "MANIFEST.csv", index=False)
    print(manifest[["file", "bytes", "rows", "cols", "dataset_id"]].to_string(index=False))
    print(f"\nWrote {len(manifest)} entries -> {RAW / 'MANIFEST.csv'}")


if __name__ == "__main__":
    main()
