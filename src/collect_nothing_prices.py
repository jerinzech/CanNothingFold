"""Collect Nothing's official store prices for its main markets.

The Nothing store is Shopify-hosted.  Product/collection JSON endpoints are
disabled, so this scraper reads the server-rendered collection page and pulls
the model name + displayed price from each product card.  It stores the raw
parse in data/raw/ and a tidy table in data/enrichment/.

Run:  .venv/bin/python src/collect_nothing_prices.py
"""

from __future__ import annotations

import csv
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
ENRICH = ROOT / "data" / "enrichment"

# host -> (country, ISO currency, currency symbol used on the page)
STORES = {
    "nothing.tech": ("United Kingdom", "GBP", "£"),
    "us.nothing.tech": ("United States", "USD", "$"),
    "de.nothing.tech": ("Germany", "EUR", "€"),
    "fr.nothing.tech": ("France", "EUR", "€"),
    "es.nothing.tech": ("Spain", "EUR", "€"),
    "it.nothing.tech": ("Italy", "EUR", "€"),
    "jp.nothing.tech": ("Japan", "JPY", "¥"),
    "au.nothing.tech": ("Australia", "AUD", "$"),
    "nl.nothing.tech": ("Netherlands", "EUR", "€"),
    "at.nothing.tech": ("Austria", "EUR", "€"),
    "be.nothing.tech": ("Belgium", "EUR", "€"),
    "pt.nothing.tech": ("Portugal", "EUR", "€"),
    "ie.nothing.tech": ("Ireland", "EUR", "€"),
    "fi.nothing.tech": ("Finland", "EUR", "€"),
    "mx.nothing.tech": ("Mexico", "MXN", "$"),
}


def fetch(host: str) -> str:
    url = f"https://{host}/collections/phones"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        return response.read().decode("utf-8", "ignore")


def parse_price(text: str) -> float | None:
    """'£1,299' -> 1299.0; '€1.299,00' -> 1299.0."""
    cleaned = re.sub(r"[^\d,.]", "", text)
    if not cleaned:
        return None
    if "," in cleaned and "." in cleaned:
        if cleaned.rfind(",") > cleaned.rfind("."):
            cleaned = cleaned.replace(".", "").replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    elif "," in cleaned:
        # Treat a single comma as a decimal separator only when it has 2 digits.
        if re.search(r",\d{2}$", cleaned):
            cleaned = cleaned.replace(",", ".")
        else:
            cleaned = cleaned.replace(",", "")
    try:
        return float(cleaned)
    except ValueError:
        return None


def scrape(host: str) -> list[dict]:
    country, currency, symbol = STORES[host]
    html = fetch(host)
    cards = re.split(r'(?=<a class="group flex flex-col gap-4" href="/products/)', html)[1:]
    rows: list[dict] = []
    for card in cards:
        heading = re.search(r"<h3[^>]*>(.*?)</h3>", card, re.S)
        if not heading:
            continue
        model = re.sub(r"<[^>]+>", "", heading.group(1)).strip()
        model = re.sub(r"\s+", " ", model)
        if not model or "phone" not in model.lower():
            continue
        # Prices sit immediately after the h3 in the card's text block.
        tail = card[heading.end(): heading.end() + 700]
        prices = [parse_price(p) for p in re.findall(rf"{re.escape(symbol)}\s?[\d][\d.,]*", tail)]
        prices = [p for p in prices if p and p > 0]
        if not prices:
            continue
        rows.append({
            "store_host": host,
            "country": country,
            "currency": currency,
            "model": model,
            "price_local": min(prices),
            "price_local_max_variant": max(prices),
            "variants_seen": len(prices),
            "price_type": "official_current",
            "source": "Nothing official store",
            "source_url": f"https://{host}/collections/phones",
            "collected_at": date.today().isoformat(),
        })
    return rows


def main() -> None:
    ENRICH.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    all_rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(scrape, host): host for host in STORES}
        for future in as_completed(futures):
            host = futures[future]
            try:
                rows = future.result()
                print(f"{host:22} {len(rows):2} models with visible prices", flush=True)
                all_rows.extend(rows)
            except Exception as exc:  # network failures should not kill the whole run
                print(f"{host:22} FAILED: {type(exc).__name__}: {exc}", flush=True)

    # De-duplicate model x country, keeping the cheapest card (base variant).
    dedup: dict[tuple[str, str], dict] = {}
    for row in all_rows:
        key = (row["country"], row["model"].lower())
        if key not in dedup or row["price_local"] < dedup[key]["price_local"]:
            dedup[key] = row
    rows = sorted(dedup.values(), key=lambda r: (r["country"], r["model"]))

    raw_path = RAW / f"nothing_official_prices_{date.today().isoformat()}.csv"
    with raw_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    out_path = ENRICH / "nothing_official_current.csv"
    with out_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved {len(rows)} rows -> {raw_path}")
    print(f"Saved {len(rows)} rows -> {out_path}")


if __name__ == "__main__":
    main()
