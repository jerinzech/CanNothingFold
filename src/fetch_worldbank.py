"""Download World Bank indicators and build a country-year enrichment table.

Indicators are fetched from the public World Bank API (no key required).  The
raw JSON response is kept in data/raw/ so the build is reproducible offline.

Run:  .venv/bin/python src/fetch_worldbank.py
"""

from __future__ import annotations

import json
import urllib.request
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ENRICH = ROOT / "data" / "enrichment"

COUNTRIES = [
    "IND", "USA", "GBR", "DEU", "JPN", "ARE", "CHN", "PAK", "ESP", "FRA",
    "KOR", "SAU", "AUS", "MEX", "CAN", "BRA", "SGP", "ITA", "NLD", "IDN",
]
YEARS = "2015:2025"

INDICATORS = {
    "IT.CEL.SETS.P2": "mobile_subscriptions_per_100",
    "IT.NET.USER.ZS": "internet_users_pct",
    "IT.NET.BBND.P2": "fixed_broadband_per_100",
    "NY.GDP.PCAP.CD": "gdp_per_capita_usd",
    "NY.GDP.MKTP.CD": "gdp_current_usd",
    "SP.POP.TOTL": "population",
    "SP.URB.TOTL.IN.ZS": "urban_population_pct",
    "SL.UEM.TOTL.ZS": "unemployment_pct",
}

COUNTRY_NAMES = {
    "IND": "India", "USA": "United States", "GBR": "United Kingdom",
    "DEU": "Germany", "JPN": "Japan", "ARE": "United Arab Emirates",
    "CHN": "China", "PAK": "Pakistan", "ESP": "Spain", "FRA": "France",
    "KOR": "South Korea", "SAU": "Saudi Arabia", "AUS": "Australia",
    "MEX": "Mexico", "CAN": "Canada", "BRA": "Brazil", "SGP": "Singapore",
    "ITA": "Italy", "NLD": "Netherlands", "IDN": "Indonesia",
}


def fetch_indicator(code: str) -> list[dict]:
    cache = RAW / f"worldbank_{code}.json"
    if cache.exists():
        payload = json.loads(cache.read_text(encoding="utf-8"))
    else:
        countries = ";".join(COUNTRIES)
        url = (
            f"https://api.worldbank.org/v2/country/{countries}/indicator/{code}"
            f"?format=json&per_page=20000&date={YEARS}"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "CanNothingFold/1.0"})
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.load(response)
        cache.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Unexpected World Bank response for {code}: {payload!r}")
    return payload[1]


def main() -> None:
    ENRICH.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    raw: dict[str, list[dict]] = {}
    frames: list[pd.DataFrame] = []
    for code, name in INDICATORS.items():
        rows = fetch_indicator(code)
        raw[code] = rows
        frame = pd.DataFrame(rows)
        if frame.empty:
            continue
        frame = frame[["countryiso3code", "date", "value"]].copy()
        frame["year"] = pd.to_numeric(frame["date"], errors="coerce").astype("Int64")
        frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        frame = frame.rename(columns={"countryiso3code": "country_code", "value": name})
        frame = frame[["country_code", "year", name]]
        frames.append(frame)
        non_null = frame[name].notna().sum()
        print(f"{code:18} -> {name:32} {len(frame):4} rows, {non_null:4} values")

    wide = frames[0]
    for frame in frames[1:]:
        wide = wide.merge(frame, on=["country_code", "year"], how="outer")
    wide["country"] = wide["country_code"].map(COUNTRY_NAMES)
    wide = wide.dropna(subset=["country", "year"]).sort_values(["country", "year"])
    wide["year"] = wide["year"].astype(int)
    cols = ["country", "country_code", "year"] + [
        c for c in wide.columns if c not in {"country", "country_code", "year"}
    ]
    wide = wide[cols].reset_index(drop=True)

    raw_path = RAW / f"worldbank_indicators_{date.today().isoformat()}.json"
    raw_path.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
    out_path = ENRICH / "enrichment_wb.csv"
    wide.to_csv(out_path, index=False)

    # Latest non-null value per country for easy joining in notebooks.
    latest = (
        wide.sort_values("year")
        .groupby("country", as_index=False)
        .last()
    )
    latest_path = ENRICH / "enrichment_wb_latest.csv"
    latest.to_csv(latest_path, index=False)

    print(f"\nSaved raw JSON -> {raw_path}")
    print(f"Saved {wide.shape[0]} country-year rows -> {out_path}")
    print(f"Saved {latest.shape[0]} country rows -> {latest_path}")


if __name__ == "__main__":
    main()
