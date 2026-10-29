"""Run the prediction markets analysis.

Usage (from the project folder):
    python src/fetch.py          # once, downloads the data
    python src/run_analysis.py

Loads data/markets.csv into MySQL, runs every query in sql/ in order, saves each result
to outputs/, writes the headline numbers to outputs/summary.json and draws the charts.
MySQL connection settings: see src/db.py.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

import db
from charts import draw_all

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


DATABASE = "prediction_markets"


def run_sql() -> dict[str, pd.DataFrame]:
    raw = ROOT / "data" / "markets.csv"
    if not raw.exists():
        raise SystemExit("Missing data. Run: python src/fetch.py")
    db.load_csv(DATABASE, "raw_markets", raw)
    con = db.connect(DATABASE)
    results = {}
    for f in sorted((ROOT / "sql").glob("*.sql")):
        df = db.run_file(con, f)
        if f.name.startswith("01_"):
            continue
        name = f.stem.split("_", 1)[1]
        df.to_csv(OUT / f"{name}.csv", index=False)
        results[name] = df
    results["_counts"] = db.query(con, """
        SELECT count(DISTINCT market_id) AS markets, count(*) AS forecasts,
               round(100 * avg((price_yes < 0.10) * 1e0), 1) AS pct_forecasts_under_10
        FROM forecasts""")
    return results


def summarise(r: dict[str, pd.DataFrame]) -> dict:
    h = r["score_by_horizon"].set_index("horizon_days")
    u = r["underdogs"].set_index("price_group")
    t = r["score_by_topic"].set_index("category")
    c = r["_counts"].iloc[0]
    return {
        "markets": int(c.markets),
        "forecasts": int(c.forecasts),
        "pct_forecasts_under_10": float(c.pct_forecasts_under_10),
        "same_markets_all_horizons": int(h.loc[1, "markets"]),
        "brier_30_days": float(h.loc[30, "brier"]),
        "brier_7_days": float(h.loc[7, "brier"]),
        "brier_1_day": float(h.loc[1, "brier"]),
        "underdog_forecasts": int(u.loc["2. 10 to 40%", "forecasts"]),
        "underdog_price_pct": float(u.loc["2. 10 to 40%", "avg_price_pct"]),
        "underdog_happened_pct": float(u.loc["2. 10 to 40%", "happened_pct"]),
        "brier_close_calls_by_topic": t.brier_unsure_markets.to_dict(),
    }


def main() -> None:
    results = run_sql()
    summary = summarise(results)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    draw_all(results, ROOT / "charts")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
