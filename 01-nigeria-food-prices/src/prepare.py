"""Normalise downloaded price files into one long table.

Put the downloaded files in data/raw/ (see README for links), then run:
    python src/prepare.py

Output: data/prices.parquet with columns
    date, state, market, commodity, price_type, price_ngn_per_kg, source

Column names differ between releases, so each source has a list of candidate names
below. If a file doesn't match, the script prints the columns it found: add the right
name to COLUMN_CANDIDATES and re-run.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"

COLUMN_CANDIDATES = {
    "date": ["date", "period_date", "price_date", "collection_date", "submission_date", "start_date", "#date"],
    "state": ["state", "admin_1", "admin1", "adm1_name", "state_name", "#adm1+name"],
    "market": ["market", "market_name", "lga", "admin_2", "adm2_name", "#loc+market+name"],
    "commodity": ["commodity", "product", "cm_name", "item", "#item+name"],
    "price_type": ["price_type", "pricetype", "market_type", "price_flavor", "#item+price+type"],
    "price": ["price", "value", "price_ngn", "#value"],
    "unit": ["unit", "unit_type", "um_name", "#item+unit"],
}


def pick(df: pd.DataFrame, field: str, required: bool = True) -> str | None:
    lower = {c.lower().strip(): c for c in df.columns}
    for cand in COLUMN_CANDIDATES[field]:
        if cand in lower:
            return lower[cand]
    if required:
        raise SystemExit(f"Can't find a '{field}' column. Columns found: {list(df.columns)}\n"
                         f"Add the right name to COLUMN_CANDIDATES['{field}'] in src/prepare.py.")
    return None


def per_kg(price: pd.Series, unit: pd.Series | None) -> pd.Series:
    """Convert to naira per kg where the unit says so; leave per-kg prices unchanged."""
    if unit is None:
        return price
    u = unit.astype(str).str.lower()
    factor = pd.Series(1.0, index=price.index)
    factor[u.str.contains(r"\b100\s*kg")] = 100
    factor[u.str.contains(r"\b50\s*kg")] = 50
    factor[u.str.contains(r"\b25\s*kg")] = 25
    factor[u.str.contains(r"\b5\s*kg")] = 5
    return price / factor


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False) if path.suffix == ".csv" else pd.read_excel(path)
    # HDX files often carry a second header row of HXL tags (#date, #value, ...): drop it
    if len(df) and str(df.iloc[0, 0]).startswith("#"):
        df = df.iloc[1:]
    cols = {f: pick(df, f, required=f not in ("price_type", "unit", "market")) for f in COLUMN_CANDIDATES}
    commodity = df[cols["commodity"]].astype(str)
    if commodity.nunique() == 1 and path.stem.startswith("level2_price_"):
        commodity = pd.Series(path.stem.removeprefix("level2_price_").replace("_", " "), index=df.index)
    out = pd.DataFrame({
        "date": pd.to_datetime(df[cols["date"]], errors="coerce"),
        "state": df[cols["state"]].astype(str).str.strip().str.title(),
        "market": df[cols["market"]].astype(str) if cols["market"] else None,
        "commodity": commodity.str.strip().str.lower(),
        "price_type": df[cols["price_type"]].astype(str).str.lower() if cols["price_type"] else "retail",
        "price_ngn_per_kg": per_kg(pd.to_numeric(df[cols["price"]], errors="coerce"),
                                   df[cols["unit"]] if cols["unit"] else None),
        "source": path.name,
    })
    return out.dropna(subset=["date", "price_ngn_per_kg"])


def main() -> None:
    files = sorted([*RAW.glob("*.csv"), *RAW.glob("*.xlsx")])
    if not files:
        raise SystemExit(f"No files in {RAW}. See README for download links.")
    frames = []
    for f in files:
        d = load(f)
        print(f"{f.name}: {len(d):,} rows, {d.commodity.nunique()} commodities, "
              f"{d.date.min():%Y-%m-%d} to {d.date.max():%Y-%m-%d}")
        frames.append(d)
    prices = pd.concat(frames, ignore_index=True)

    # Remove obvious entry errors: outside 1st-99th percentile within commodity x price type
    q = prices.groupby(["commodity", "price_type"]).price_ngn_per_kg.quantile([0.01, 0.99]).unstack()
    prices = prices.join(q, on=["commodity", "price_type"])
    before = len(prices)
    prices = prices[prices.price_ngn_per_kg.between(prices[0.01], prices[0.99])].drop(columns=[0.01, 0.99])
    print(f"removed {before - len(prices):,} outlier rows ({100 * (before - len(prices)) / before:.1f}%)")

    prices.to_parquet(ROOT / "data" / "prices.parquet", index=False)
    print(f"wrote {len(prices):,} rows to data/prices.parquet")


if __name__ == "__main__":
    main()
