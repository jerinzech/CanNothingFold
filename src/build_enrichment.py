"""Build the compiled price and market enrichment tables.

Inputs (data/raw/):
  phone_information_2024.csv   D01 core marketplace prices (UK/DE/US)
  mobiles_2025.csv             D03 five-country launch prices
  spain_prices.csv             D11 Spain retail prices
  specs_india_2026.csv         D08 India 91mobiles retail
  specs_india_2025.csv         D29 India retail
  specs_india_2025_basic.csv   D27 India retail
  specs_india_2026_alt.csv     D14 India 2026 (unverified holdout)
  nothing_official_prices_*.csv  official store snapshot
  nothing_launch_prices_manual.csv  hand-verified launch anchors

Outputs (data/enrichment/):
  price_by_country.csv
  foldable_prices.csv
  nothing_prices.csv
  nothing_prices_template.csv
  enrichment_market.csv
  enrichment_market_country.csv
  (enrichment_wb.csv is built by src/fetch_worldbank.py)

Outputs (results/):
  country_price_index.csv

Run:  .venv/bin/python src/build_enrichment.py
"""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ENRICH = ROOT / "data" / "enrichment"
RESULTS = ROOT / "results"
for directory in (ENRICH, RESULTS):
    directory.mkdir(parents=True, exist_ok=True)

# Fixed FX assumptions from the project plan.  EUR per one unit of local currency.
FX_ASOF = "2026-10-29"
EUR_PER_UNIT = {
    "EUR": 1.0,
    "USD": 0.92,
    "GBP": 1.17,
    "INR": 0.0104,
    "PKR": 0.0032,
    "CNY": 0.128,
    "AED": 0.250,
    "JPY": 0.0060,
    "AUD": 0.63,
    "MXN": 0.048,
    "CAD": 0.68,
}
EUR_PER_USD = EUR_PER_UNIT["USD"]

COUNTRY_CURRENCY = {
    "India": "INR",
    "United Kingdom": "GBP",
    "Germany": "EUR",
    "United States": "USD",
    "United Arab Emirates": "AED",
    "Japan": "JPY",
    "Spain": "EUR",
    "France": "EUR",
    "Italy": "EUR",
    "China": "CNY",
    "Pakistan": "PKR",
    "Australia": "AUD",
    "Mexico": "MXN",
}

FOLDABLE_RE = re.compile(r"\b(?:fold|flip|razr)\b", flags=re.IGNORECASE)

KAGGLE = {
    "D01": "https://www.kaggle.com/datasets/willianoliveiragibin/phone-information-2024",
    "D03": "https://www.kaggle.com/datasets/abdulmalik1518/mobiles-dataset-2025",
    "D08": "https://www.kaggle.com/datasets/suresh2837/smartphone-specifications-and-prices-2026",
    "D11": "https://www.kaggle.com/datasets/juanmerinobermejo/spain-smartphones-dataset",
    "D14": "https://www.kaggle.com/datasets/abhishekmondal/indian-smartphones-dataset-2026",
    "D27": "https://www.kaggle.com/datasets/rohsanyadav/smartphones-dataset",
    "D29": "https://www.kaggle.com/datasets/vashisthrahul13/mobile-price-and-specs-2025",
}

BRANDS = [
    "Nothing", "CMF", "Apple", "Samsung", "Xiaomi", "Redmi", "POCO", "OnePlus",
    "OPPO", "vivo", "iQOO", "realme", "Motorola", "Nokia", "Google", "Honor",
    "Huawei", "Infinix", "Tecno", "Itel", "Lava", "Micromax", "Asus", "Sony",
    "LG", "HTC", "ZTE", "Lenovo",
]


def to_usd(amount: float | int | None, currency: str) -> float | None:
    if amount is None or pd.isna(amount):
        return None
    rate = EUR_PER_UNIT.get(currency)
    if rate is None:
        return None
    return round(float(amount) * rate / EUR_PER_USD, 2)


def to_eur(amount: float | int | None, currency: str) -> float | None:
    if amount is None or pd.isna(amount):
        return None
    rate = EUR_PER_UNIT.get(currency)
    if rate is None:
        return None
    return round(float(amount) * rate, 2)


def parse_brand_model(name: str) -> tuple[str, str]:
    text = str(name).strip()
    low = text.lower()
    if "nothing" in low or low.startswith("cmf"):
        return "Nothing", text
    for brand in BRANDS:
        if low.startswith(brand.lower()):
            return brand, text[len(brand):].strip(" -")
    first = text.split()[0] if text.split() else "Unknown"
    return first.title(), text


def normalize_model(model: str, brand: str | None = None) -> str:
    text = str(model).lower()
    if brand:
        text = re.sub(rf"^\s*{re.escape(brand.lower())}\s*", "", text)
    text = text.replace("&", " and ")
    # Join split suffixes: "Phone 4(b)" -> "Phone 4b", "Phone (2a)" stays.
    text = re.sub(r"(\d)\s*\(\s*([a-z])\s*\)", r"\1\2", text)
    # Keep model numbers inside parentheses: Phone (2a) -> phone 2a, not phone.
    text = text.replace("(", " ").replace(")", " ")
    # Strip storage/RAM qualifiers, e.g. "8gb", "128 gb", "12+256gb".
    text = re.sub(r"\b\d+\s*\+\s*\d+\s*(?:gb|tb)?\b", " ", text)
    text = re.sub(r"\b\d+\s*(?:gb|tb)\b", " ", text)
    text = re.sub(r"\b(?:ram|rom|storage|5g|4g|lte|dual sim)\b", " ", text)
    text = text.replace("+", " ")
    text = re.sub(r"[^a-z0-9+ ]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def model_id(brand: str, key: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", f"{brand} {key}".lower()).strip("-")
    return slug


def parse_money(value: object, default_currency: str | None = None) -> tuple[float | None, str | None]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None, default_currency
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value), default_currency
    text = str(value).strip()
    if not text or text.lower() in {"not available", "nan", "none", "-"}:
        return None, default_currency
    token = re.search(r"\b(USD|EUR|GBP|INR|PKR|CNY|AED|JPY|AUD|MXN|CAD)\b", text, re.I)
    currency = token.group(1).upper() if token else default_currency
    if currency is None:
        symbol = re.search(r"[₹£€$¥]", text)
        currency = {"₹": "INR", "£": "GBP", "€": "EUR", "$": "USD", "¥": "JPY"}.get(
            symbol.group(0) if symbol else "", default_currency
        )
    number = re.search(r"[\d][\d,]*(?:\.\d+)?", text)
    if not number:
        return None, currency
    cleaned = number.group(0)
    if "," in cleaned and "." not in cleaned:
        # "396,22" is a decimal comma; "79,999" is a thousands separator.
        cleaned = cleaned.replace(",", ".") if re.search(r",\d{2}$", cleaned) else cleaned.replace(",", "")
    else:
        cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned), currency
    except ValueError:
        return None, currency


def release_year_from_text(value: object) -> float | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    match = re.search(r"(19|20)\d{2}", str(value))
    return float(match.group(0)) if match else None


def release_year_for_nothing(model: str) -> float | None:
    key = normalize_model(model, "Nothing")
    mapping = [
        ("phone 4a pro", 2026), ("phone 4a", 2026), ("phone 4b", 2026),
        ("cmf phone 2 pro", 2025), ("phone 3a lite", 2025), ("phone 3a pro", 2025),
        ("phone 3a", 2025), ("phone 3", 2025), ("phone 2a plus", 2024),
        ("phone 2a", 2024), ("cmf phone 1", 2024), ("phone 2", 2023),
        ("phone 1", 2022),
    ]
    for token, year in mapping:
        if token in key:
            return float(year)
    return None


def make_frame(rows: list[dict]) -> pd.DataFrame:
    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    for column in ("release_year",):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    frame["is_foldable"] = frame["is_foldable"].astype(bool)
    return frame


def aggregate(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty:
        return frame
    grouped = (
        frame.groupby(
            ["source", "country", "model_key", "brand", "model", "release_year",
             "is_foldable", "price_type", "currency", "source_url", "collected_at",
             "verified", "source_status"],
            dropna=False,
        )
        .agg(
            local_price=("local_price", "median"),
            price_usd=("price_usd", "median"),
            price_eur=("price_eur", "median"),
            n_listings=("local_price", "size"),
            local_price_min=("local_price", "min"),
            local_price_max=("local_price", "max"),
        )
        .reset_index()
    )
    grouped["model_id"] = [
        model_id(brand, key) for brand, key in zip(grouped["brand"], grouped["model_key"])
    ]
    return grouped


# ---------------------------------------------------------------------------
# Source loaders
# ---------------------------------------------------------------------------

def load_d01() -> pd.DataFrame:
    path = RAW / "phone_information_2024.csv"
    df = pd.read_csv(path, low_memory=False)
    store_country = {"Amazon UK": "United Kingdom", "Amazon DE": "Germany", "Amazon US": "United States"}
    df = df[df["store"].isin(store_country)].copy()
    rows = []
    for _, row in df.iterrows():
        country = store_country[row["store"]]
        currency = str(row["currency"]).upper()
        brand = str(row["phone_brand"]).strip().title()
        if brand.lower() == "nothing":
            brand = "Nothing"
        local = float(row["price"])
        rows.append({
            "source": "D01 phone_information_2024",
            "source_url": KAGGLE["D01"],
            "country": country,
            "brand": brand,
            "model": str(row["phone_model"]).strip(),
            "model_key": normalize_model(row["phone_model"], brand),
            "release_year": row.get("Year"),
            "is_foldable": bool(row.get("Foldable", 0)),
            "currency": currency,
            "local_price": local,
            "price_usd": to_usd(local, currency),
            "price_eur": to_eur(local, currency),
            "price_type": "marketplace",
            "collected_at": "2024-10-20",
            "verified": True,
            "source_status": "verified",
        })
    frame = make_frame(rows)
    return aggregate(frame)


def load_d03() -> pd.DataFrame:
    path = RAW / "mobiles_2025.csv"
    df = pd.read_csv(path, encoding="latin-1", low_memory=False)
    columns = {
        "Pakistan": "Launched Price (Pakistan)",
        "India": "Launched Price (India)",
        "China": "Launched Price (China)",
        "United States": "Launched Price (USA)",
        "United Arab Emirates": "Launched Price (Dubai)",
    }
    df["model_key"] = [
        normalize_model(m, b) for m, b in zip(df["Model Name"], df["Company Name"])
    ]
    df["release_year"] = pd.to_numeric(df["Launched Year"], errors="coerce")
    df.loc[df["release_year"] > 2026, "release_year"] = 2024

    rows = []
    for country, column in columns.items():
        for _, row in df.iterrows():
            amount, currency = parse_money(row[column], COUNTRY_CURRENCY[country])
            if amount is None or amount <= 0:
                continue
            brand = str(row["Company Name"]).strip().title()
            if brand.lower() == "nothing":
                brand = "Nothing"
            key = row["model_key"]
            usd = to_usd(amount, currency or COUNTRY_CURRENCY[country])
            # Use the same row's US price, so storage variants are compared
            # like-for-like (the model_key deliberately strips storage).
            us_amount, us_currency = parse_money(row["Launched Price (USA)"], "USD")
            us_ref = to_usd(us_amount, us_currency or "USD") if us_amount is not None else None
            rows.append({
                "source": "D03 mobiles_2025",
                "source_url": KAGGLE["D03"],
                "country": country,
                "brand": brand,
                "model": str(row["Model Name"]).strip(),
                "model_key": key,
                "release_year": row["release_year"],
                "is_foldable": bool(FOLDABLE_RE.search(str(row["Model Name"]))),
                "currency": currency or COUNTRY_CURRENCY[country],
                "local_price": amount,
                "price_usd": usd,
                "price_eur": to_eur(amount, currency or COUNTRY_CURRENCY[country]),
                "price_type": "official_launch",
                "collected_at": "2025-02-18",
                "verified": True,
                "source_status": "verified",
                "us_price_usd": us_ref,
                "ratio_vs_us": (usd / us_ref) if usd and us_ref else None,
            })
    frame = make_frame(rows)
    # Aggregating across storage variants: median ratio is still a within-model
    # comparison because each row's ratio was computed against its own US variant.
    agg = aggregate(frame.drop(columns=["us_price_usd", "ratio_vs_us"]))
    ratios = (
        frame.groupby(["country", "model_key"], dropna=False)["ratio_vs_us"]
        .median()
        .reset_index()
    )
    return agg.merge(ratios, on=["country", "model_key"], how="left")


def load_d11() -> pd.DataFrame:
    df = pd.read_csv(RAW / "spain_prices.csv", low_memory=False)
    df["brand"] = df["Brand"].astype(str).str.strip()
    df.loc[df["brand"].str.lower() == "nothing", "brand"] = "Nothing"
    df["model"] = df["Model"].astype(str).str.strip()
    df["model_key"] = [normalize_model(m, b) for m, b in zip(df["model"], df["brand"])]
    df["release_year"] = [
        release_year_for_nothing(m) if b == "Nothing" else np.nan
        for m, b in zip(df["model"], df["brand"])
    ]
    rows = []
    for _, row in df.iterrows():
        price = pd.to_numeric(row["Final Price"], errors="coerce")
        if pd.isna(price) or price <= 0:
            continue
        rows.append({
            "source": "D11 Spain retail",
            "source_url": KAGGLE["D11"],
            "country": "Spain",
            "brand": row["brand"],
            "model": row["model"],
            "model_key": row["model_key"],
            "release_year": row["release_year"],
            "is_foldable": bool(FOLDABLE_RE.search(str(row["model"]))),
            "currency": "EUR",
            "local_price": float(price),
            "price_usd": to_usd(price, "EUR"),
            "price_eur": to_eur(price, "EUR"),
            "price_type": "retail",
            "collected_at": "2024-03-03",
            "verified": True,
            "source_status": "verified",
        })
    return aggregate(make_frame(rows))


def load_india_supplement(path: Path, source: str, url: str, name_col: str,
                          price_col: str, date_col: str | None,
                          brand_col: str | None, price_type: str,
                          verified: bool, status: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False)
    rows = []
    for _, row in df.iterrows():
        name = str(row[name_col]).strip()
        amount, currency = parse_money(row[price_col], "INR")
        if amount is None or amount <= 0 or not name or name.lower() == "nan":
            continue
        if brand_col and brand_col in df.columns and str(row[brand_col]).strip().lower() not in {"other", "nan"}:
            brand = str(row[brand_col]).strip().title()
        else:
            brand, _ = parse_brand_model(name)
        if "nothing" in name.lower() or brand.lower() == "nothing":
            brand = "Nothing"
        key = normalize_model(name, brand)
        year = release_year_from_text(row[date_col]) if date_col else np.nan
        if brand == "Nothing" and pd.isna(year):
            year = release_year_for_nothing(name)
        rows.append({
            "source": source,
            "source_url": url,
            "country": "India",
            "brand": brand,
            "model": name,
            "model_key": key,
            "release_year": year,
            "is_foldable": bool(FOLDABLE_RE.search(name)),
            "currency": currency or "INR",
            "local_price": amount,
            "price_usd": to_usd(amount, currency or "INR"),
            "price_eur": to_eur(amount, currency or "INR"),
            "price_type": price_type,
            "collected_at": "2026-10-29",
            "verified": verified,
            "source_status": status,
        })
    frame = make_frame(rows)
    if not frame.empty:
        # Drop obvious scrape/typo outliers (e.g. a missing digit) before
        # aggregating variants to a model-level median.
        median_price = frame.groupby("model_key")["local_price"].transform("median")
        frame = frame[frame["local_price"] >= 0.3 * median_price].copy()
    return aggregate(frame)


def load_official_current() -> pd.DataFrame:
    candidates = sorted(RAW.glob("nothing_official_prices_*.csv"))
    if not candidates:
        return pd.DataFrame()
    df = pd.read_csv(candidates[-1], low_memory=False)
    rows = []
    for _, row in df.iterrows():
        currency = str(row["currency"]).upper()
        local = float(row["price_local"])
        rows.append({
            "source": "Nothing official store",
            "source_url": row["source_url"],
            "country": row["country"],
            "brand": "Nothing",
            "model": row["model"],
            "model_key": normalize_model(row["model"], "Nothing"),
            "release_year": release_year_for_nothing(row["model"]),
            "is_foldable": bool(FOLDABLE_RE.search(str(row["model"]))),
            "currency": currency,
            "local_price": local,
            "price_usd": to_usd(local, currency),
            "price_eur": to_eur(local, currency),
            "price_type": "official_current",
            "collected_at": row["collected_at"],
            "verified": True,
            "source_status": "verified",
            "variants_seen": row.get("variants_seen"),
            "price_local_max_variant": row.get("price_local_max_variant"),
        })
    return aggregate(make_frame(rows))


# ---------------------------------------------------------------------------
# Main build
# ---------------------------------------------------------------------------

def main() -> None:
    d01 = load_d01()
    d03 = load_d03()
    d11 = load_d11()
    d08 = load_india_supplement(
        RAW / "specs_india_2026.csv", "D08 91mobiles India", KAGGLE["D08"],
        "name", "price", "release_date", None, "retail", True, "verified",
    )
    d29 = load_india_supplement(
        RAW / "specs_india_2025.csv", "D29 India 2025", KAGGLE["D29"],
        "mobile_name", "price", "release_date", None, "retail", True, "verified",
    )
    d27 = load_india_supplement(
        RAW / "specs_india_2025_basic.csv", "D27 India 2025 basic", KAGGLE["D27"],
        "Name", "Price", None, "brand_name", "retail", True, "verified",
    )
    d14 = load_india_supplement(
        RAW / "specs_india_2026_alt.csv", "D14 India 2026 alt", KAGGLE["D14"],
        "model", "price", None, "brand", "retail_unverified", False, "unverified",
    )
    official = load_official_current()

    # US reference prices for within-model ratios (median across variants).
    def us_price_map(frame: pd.DataFrame) -> dict[str, float]:
        if frame.empty:
            return {}
        subset = frame[frame["country"] == "United States"]
        return (
            subset.groupby("model_key")["price_usd"].median().dropna().to_dict()
        )

    d03_us = us_price_map(d03)
    d01_us = us_price_map(d01)
    official_us = us_price_map(official)

    def us_reference(source: str, key: str) -> float | None:
        if source.startswith("D03"):
            return d03_us.get(key) or d01_us.get(key) or official_us.get(key)
        if source.startswith("D01"):
            return d01_us.get(key) or d03_us.get(key) or official_us.get(key)
        if source.startswith("Nothing official"):
            # Only compare the same model in the same current-price snapshot.
            return official_us.get(key)
        return d03_us.get(key) or d01_us.get(key) or official_us.get(key)

    frames = [d01, d03, d11, d08, d29, d27, d14, official]
    frames = [f for f in frames if not f.empty]
    compiled = pd.concat(frames, ignore_index=True, sort=False)
    compiled["us_price_usd"] = [
        us_reference(src, key) for src, key in zip(compiled["source"], compiled["model_key"])
    ]
    computed_ratio = np.where(
        compiled["us_price_usd"].notna() & compiled["price_usd"].notna(),
        compiled["price_usd"] / compiled["us_price_usd"],
        np.nan,
    )
    # D03 already stores a like-for-like ratio against the same storage
    # variant's US price; keep it instead of replacing it with a model median.
    is_d03 = compiled["source"].astype(str).str.startswith("D03")
    compiled["ratio_vs_us"] = np.where(is_d03, compiled["ratio_vs_us"], computed_ratio)
    # For US rows the ratio is exactly 1 (avoid tiny FX artefacts).
    compiled.loc[compiled["country"] == "United States", "ratio_vs_us"] = 1.0

    output_columns = [
        "model_id", "brand", "model", "release_year", "is_foldable", "country",
        "currency", "local_price", "price_usd", "price_eur", "price_type",
        "source", "source_url", "collected_at", "n_listings", "local_price_min",
        "local_price_max", "us_price_usd", "ratio_vs_us", "verified",
        "source_status", "model_key",
    ]
    compiled = compiled[output_columns].sort_values(
        ["country", "brand", "model", "source", "price_type"]
    )
    compiled.to_csv(ENRICH / "price_by_country.csv", index=False)
    print(f"[save] price_by_country.csv          {len(compiled):>7,} rows")

    foldables = compiled[compiled["is_foldable"]].copy()
    foldables.to_csv(ENRICH / "foldable_prices.csv", index=False)
    print(f"[save] foldable_prices.csv           {len(foldables):>7,} rows")

    # Nothing-only price table, including hand-verified launch anchors.
    nothing = compiled[compiled["brand"].astype(str).str.lower() == "nothing"].copy()
    launch_path = ENRICH / "nothing_launch_prices_manual.csv"
    if launch_path.exists():
        launch = pd.read_csv(launch_path)
        for column in ("price_usd", "price_eur", "ratio_vs_us", "us_price_usd"):
            if column not in launch.columns:
                launch[column] = np.nan
        launch["brand"] = "Nothing"
        launch["price_type"] = "official_launch"
        launch["model_key"] = [
            normalize_model(m, "Nothing") for m in launch["model"]
        ]
        launch["model_id"] = [
            model_id("Nothing", key) for key in launch["model_key"]
        ]
        launch["is_foldable"] = launch["model"].astype(str).str.contains(FOLDABLE_RE)
        launch["release_year"] = [
            release_year_for_nothing(m) for m in launch["model"]
        ]
        launch["n_listings"] = 1
        launch["local_price_min"] = launch["local_price"]
        launch["local_price_max"] = launch["local_price"]
        launch["price_usd"] = [
            to_usd(p, c) for p, c in zip(launch["local_price"], launch["currency"])
        ]
        launch["price_eur"] = [
            to_eur(p, c) for p, c in zip(launch["local_price"], launch["currency"])
        ]
        manual_us = (
            launch[launch["country"] == "United States"]
            .groupby("model_key")["price_usd"].median()
            .to_dict()
        )
        launch["us_price_usd"] = [
            manual_us.get(key) or us_reference("manual_launch", key)
            for key in launch["model_key"]
        ]
        launch["ratio_vs_us"] = launch["price_usd"] / launch["us_price_usd"]
        launch.loc[launch["country"] == "United States", "ratio_vs_us"] = 1.0
        launch["verified"] = True
        launch["source_status"] = "verified"
        nothing = pd.concat([nothing, launch[output_columns]], ignore_index=True, sort=False)
        nothing = nothing.drop_duplicates(
            subset=["model_key", "country", "price_type"], keep="last"
        )
    nothing = nothing.sort_values(["model", "country", "price_type"])
    nothing.to_csv(ENRICH / "nothing_prices.csv", index=False)
    print(f"[save] nothing_prices.csv            {len(nothing):>7,} rows")

    # Collection template: every target market x model, with gaps visible.
    target_countries = [
        "India", "United Kingdom", "Germany", "United States",
        "United Arab Emirates", "Japan", "Spain", "France",
    ]
    target_models = [
        "Phone (1)", "Phone (2)", "Phone (2a)", "Phone (2a) Plus", "CMF Phone 1",
        "Phone (3)", "Phone (3a)", "Phone (3a) Pro", "Phone (3a) Lite",
        "Phone (4a)", "Phone (4a) Pro", "Phone (4b)", "CMF Phone 2 Pro",
    ]
    template_rows = []
    for model in target_models:
        key = normalize_model(model, "Nothing")
        for country in target_countries:
            existing = nothing[
                (nothing["model_key"] == key)
                & (nothing["country"] == country)
                & (nothing["price_type"] != "retail_unverified")
            ]
            if existing.empty:
                template_rows.append({
                    "model": model, "release_year": release_year_for_nothing(model),
                    "country": country, "status": "need", "price_type": "",
                    "local_price": np.nan, "currency": COUNTRY_CURRENCY[country],
                    "source": "", "source_url": "",
                    "notes": "Collect official launch price with source URL.",
                })
            else:
                best = existing.sort_values(
                    "price_type", key=lambda s: s.map({
                        "official_launch": 0, "official_current": 1,
                        "retail": 2, "marketplace": 3,
                    }).fillna(9)
                ).iloc[0]
                template_rows.append({
                    "model": model, "release_year": release_year_for_nothing(model),
                    "country": country,
                    "status": "have" if best["price_type"] == "official_launch" else "have_current",
                    "price_type": best["price_type"], "local_price": best["local_price"],
                    "currency": best["currency"], "source": best["source"],
                    "source_url": best["source_url"],
                    "notes": "" if best["price_type"] == "official_launch" else "Launch price still missing; current/retail price shown.",
                })
    template = pd.DataFrame(template_rows)
    template.to_csv(ENRICH / "nothing_prices_template.csv", index=False)
    print(f"[save] nothing_prices_template.csv   {len(template):>7,} rows")

    # Country price index: within-model ratios, verified rows only.
    verified = compiled[compiled["verified"] & compiled["ratio_vs_us"].notna()].copy()
    index_rows = []
    for (country, foldable, price_type), group in verified.groupby(
        ["country", "is_foldable", "price_type"]
    ):
        index_rows.append({
            "country": country, "segment": "foldable" if foldable else "all_models",
            "price_type": price_type,
            "n": len(group), "median_ratio_vs_us": group["ratio_vs_us"].median(),
            "mean_ratio_vs_us": group["ratio_vs_us"].mean(),
            "p25_ratio_vs_us": group["ratio_vs_us"].quantile(0.25),
            "p75_ratio_vs_us": group["ratio_vs_us"].quantile(0.75),
        })
    index = pd.DataFrame(index_rows).sort_values(["segment", "price_type", "country"])
    index.to_csv(RESULTS / "country_price_index.csv", index=False)
    print(f"[save] results/country_price_index.csv {len(index):>5,} rows")

    # Market enrichment (global, one row per year) and country-level seed.
    market = pd.DataFrame([
        {
            "year": 2023, "global_smartphone_shipments_m": 1166.0,
            "global_foldable_shipments_m": 18.1, "foldable_share_pct": 1.55,
            "source": "IDC (2023 smartphone shipments; foldable shipments)",
            "source_url": "https://www.idc.com/promo/smartphone-market-share/",
            "status": "secondary",
            "notes": "Foldable share is derived (18.1 / 1166).",
        },
        {
            "year": 2024, "global_smartphone_shipments_m": 1232.0,
            "global_foldable_shipments_m": 18.7, "foldable_share_pct": 1.52,
            "source": "IDC (2024 smartphone shipments; foldable shipments implied by 2025 +10% guide)",
            "source_url": "https://my.idc.com/getdoc.jsp?containerId=prUS54017625",
            "status": "derived",
            "notes": "Foldable 2024 implied from IDC's 2025 forecast (+10% YoY).",
        },
        {
            "year": 2025, "global_smartphone_shipments_m": 1250.0,
            "global_foldable_shipments_m": 20.6, "foldable_share_pct": 1.65,
            "source": "Omdia (smartphone shipments); IDC (foldable shipments)",
            "source_url": "https://omdia.tech.informa.com/pr/2026/jan/global-smartphone-market-grew-2percent-in-2025-while-memory-headwinds-set-the-stage-for-a-challenging-2026",
            "status": "verified",
            "notes": "Foldable share is derived (20.6 / 1250).",
        },
    ])
    market.to_csv(ENRICH / "enrichment_market.csv", index=False)
    print(f"[save] enrichment_market.csv         {len(market):>7,} rows")

    country_market = pd.DataFrame([
        ["Global", 2025, "smartphone_shipments_m", 1250.0, "million units", "Omdia", "https://omdia.tech.informa.com/pr/2026/jan/global-smartphone-market-grew-2percent-in-2025-while-memory-headwinds-set-the-stage-for-a-challenging-2026", "verified", ""],
        ["Global", 2025, "foldable_shipments_m", 20.6, "million units", "IDC", "https://my.idc.com/getdoc.jsp?containerId=prUS54017625", "verified", ""],
        ["Global", 2025, "foldable_share_pct", 1.65, "percent", "Derived from Omdia + IDC", "", "derived", "20.6 / 1250"],
        ["Global", 2025, "nothing_shipments_m", 3.0, "million units", "Omdia", "https://omdia.tech.informa.com/pr/2026/jan/global-smartphone-market-grew-2percent-in-2025-while-memory-headwinds-set-the-stage-for-a-challenging-2026", "verified", "Omdia: Nothing grew 86% and surpassed 3 million units in 2025"],
        ["Global", 2025, "nothing_yoy_growth_pct", 86.0, "percent", "Omdia", "https://omdia.tech.informa.com/pr/2026/jan/global-smartphone-market-grew-2percent-in-2025-while-memory-headwinds-set-the-stage-for-a-challenging-2026", "verified", ""],
        ["India", 2025, "smartphone_shipments_m", 154.2, "million units", "Omdia", "https://omdia.tech.informa.com/pr/2026/jan/indias-smartphone-shipments-fell-by-1percent-in-2025-amid-softer-demand-and-cost-pressures-vivo-remains-market-leader", "verified", ""],
        ["India", 2025, "foldable_shipments_m", np.nan, "million units", "", "", "to_fill", "IDC/Counterpoint country foldable tracker; paywalled"],
        ["India", 2025, "nothing_market_share_pct", np.nan, "percent", "", "", "to_fill", "Counterpoint/Omdia India vendor tracker"],
        ["China", 2025, "foldable_shipments_m", 10.01, "million units", "IDC (via Mordor Intelligence)", "https://www.mordorintelligence.com/industry-reports/foldable-smartphone-market", "secondary", "China foldables +9.2% YoY in 2025"],
        ["Europe", 2025, "smartphone_shipments_m", 134.2, "million units", "Omdia", "https://www.businesswire.com/news/home/20260223432918/en/Omdia-Apple-and-HONOR-Claim-Record-Market-Shares-as-Europes-Smartphone-Shipment-Dips-1-in-2025", "verified", "Europe declined 1% in 2025"],
        ["Middle East", 2025, "smartphone_shipments_m", 54.8, "million units", "Omdia", "https://omdia.tech.informa.com/pr/2026/feb/middle-east-smartphone-market-grows-13eprcent-in-2025-memory-pressures-to-weigh-on-2026-outlook", "verified", "Excludes Turkey"],
        ["United States", 2025, "smartphone_shipments_m", 161.0, "million units", "MarketDataForecast (secondary)", "https://www.marketdataforecast.com/market-reports/united-states-smartphone-market", "secondary", "Cross-check against IDC/Counterpoint before publishing"],
        ["Japan", 2024, "smartphone_shipments_m", 31.9, "million units", "Accio (secondary)", "https://www.accio.com/business/best-selling-phone-in-japan-2025", "secondary", "2025 value still to_fill"],
        ["United Kingdom", 2025, "smartphone_shipments_m", np.nan, "million units", "", "", "to_fill", "Omdia/Counterpoint UK tracker; 14.0M widely cited for 2023"],
        ["Germany", 2025, "smartphone_shipments_m", np.nan, "million units", "", "", "to_fill", "Omdia/Counterpoint Germany tracker"],
        ["United Arab Emirates", 2025, "smartphone_shipments_m", np.nan, "million units", "", "", "to_fill", "Omdia Middle East report gives regional 54.8M only"],
        ["Spain", 2025, "smartphone_shipments_m", np.nan, "million units", "", "", "to_fill", "Omdia Europe report gives regional 134.2M only"],
        ["France", 2025, "smartphone_shipments_m", np.nan, "million units", "", "", "to_fill", "Omdia Europe report gives regional 134.2M only"],
    ], columns=["country", "year", "metric", "value", "unit", "source", "source_url", "status", "notes"])
    country_market.to_csv(ENRICH / "enrichment_market_country.csv", index=False)
    print(f"[save] enrichment_market_country.csv {len(country_market):>7,} rows")

    print("\nCountry price index (verified rows):")
    print(index.to_string(index=False))


if __name__ == "__main__":
    main()
