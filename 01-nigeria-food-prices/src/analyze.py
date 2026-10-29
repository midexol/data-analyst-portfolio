"""Nigeria food prices 2019-2026 from the World Bank's monthly market price estimates.

Put the World Bank CSV (NGA_RTFP_mkt_*.csv) in data/raw/ and run:
    python src/analyze.py

Loads the CSV into MySQL, runs every query in sql/ in order, saves each result to outputs/,
writes the headline numbers to outputs/summary.json and draws the charts.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import db
from charts import draw_all

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SQL = ROOT / "sql"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


DATABASE = "food_prices"


def connect():
    files = sorted(RAW.glob("NGA_RTFP_mkt_*.csv"))
    if not files:
        raise SystemExit(f"Put the World Bank NGA_RTFP_mkt_*.csv file in {RAW} (see README).")
    rows = db.load_csv(DATABASE, "raw_prices", files[-1], low_memory=False)
    print(f"loaded {rows:,} rows into raw_prices")
    return db.connect(DATABASE), files[-1]


def run_sql(con) -> dict[str, pd.DataFrame]:
    results = {}
    for f in sorted(SQL.glob("*.sql")):
        df = db.run_file(con, f)
        if f.name.startswith("01_"):
            continue  # staging: builds tables, returns nothing
        name = f.stem.split("_", 1)[1]  # 02_national_index -> national_index
        df.to_csv(OUT / f"{name}.csv", index=False)
        results[name] = df
    return results


def summarise(con, r: dict[str, pd.DataFrame], source: Path) -> dict:
    ni = r["national_index"].set_index("date")
    ni.index = pd.to_datetime(ni.index)
    gi = r["group_index"].set_index("date")
    gi.index = pd.to_datetime(gi.index)
    pz = r["plate_by_zone"].set_index("zone")
    peak = ni.yoy_inflation_pct.idxmax()
    markets = db.query(con, "SELECT count(DISTINCT market) AS n FROM prices WHERE is_real_market").n[0]
    return {
        "source_file": source.name,
        "months": ["2019-01", ni.index.max().strftime("%Y-%m")],
        "real_markets": int(markets),
        "peak_yoy_inflation_pct": round(float(ni.yoy_inflation_pct.max()), 1),
        "peak_yoy_month": peak.strftime("%Y-%m"),
        "latest_yoy_inflation_pct": round(float(ni.yoy_inflation_pct.iloc[-1]), 1),
        "first_negative_yoy_month": ni[(ni.index > peak) & (ni.yoy_inflation_pct < 0)].index.min().strftime("%Y-%m"),
        "index_jul_2026_vs_jan_2023": round(float(ni.food_price_index.iloc[-1] / ni.loc["2023-01-01", "food_price_index"]), 2),
        "grains_index_peak": float(gi.iloc[:, 0].max()),
        "grains_index_peak_month": gi.iloc[:, 0].idxmax().strftime("%Y-%m"),
        "grains_index_now": float(gi.iloc[-1, 0]),
        "protein_index_peak": float(gi.iloc[:, 1].max()),
        "protein_index_peak_month": gi.iloc[:, 1].idxmax().strftime("%Y-%m"),
        "protein_index_now": float(gi.iloc[-1, 1]),
        "plate_peak_month": pz.peak_month.iloc[0],
        "plate_jul_2026_by_zone": pz.plate_jul_2026.to_dict(),
        "pct_prices_observed_2019_2026": round(float(db.query(
            con, "SELECT 100 * avg(foods_observed * 1e0) / 16 AS pct FROM prices WHERE is_real_market").pct[0]), 1),
    }


def main() -> None:
    con, source = connect()
    results = run_sql(con)
    summary = summarise(con, results, source)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    draw_all(results, ROOT / "charts")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
