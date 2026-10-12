"""Run the full Olist delivery-vs-reviews analysis.

Usage (from the project folder):
    python src/run_analysis.py

Reads the raw CSVs in data/raw/, runs every file in sql/ in order with DuckDB,
writes each result to outputs/, runs the statistical tests, draws the charts
into charts/, and writes outputs/summary.json with the headline numbers.
"""
from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SQL = ROOT / "sql"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

RAW_TABLES = {
    "raw_orders": "olist_orders_dataset.csv",
    "raw_reviews": "olist_order_reviews_dataset.csv",
    "raw_customers": "olist_customers_dataset.csv",
    "raw_items": "olist_order_items_dataset.csv",
}


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name, file in RAW_TABLES.items():
        path = RAW / file
        if not path.exists():
            raise SystemExit(f"Missing {path}. See data/README.md for how to download the data.")
        con.sql(f"CREATE OR REPLACE VIEW {name} AS SELECT * FROM read_csv_auto('{path.as_posix()}')")
    return con


def run_sql(con: duckdb.DuckDBPyConnection) -> dict[str, pd.DataFrame]:
    results: dict[str, pd.DataFrame] = {}
    for f in sorted(SQL.glob("*.sql")):
        text = f.read_text()
        if f.name.startswith("01_"):
            con.execute(text)  # staging: creates tables, returns nothing
            continue
        df = con.sql(text).df()
        df.to_csv(OUT / f"{f.stem}.csv", index=False)
        results[f.stem] = df
    return results


def tests(con: duckdb.DuckDBPyConnection) -> dict:
    df = con.sql("SELECT is_late, review_score FROM fct_orders WHERE review_score IS NOT NULL").df()
    on_time = df.loc[~df.is_late, "review_score"]
    late = df.loc[df.is_late, "review_score"]
    u, p = stats.mannwhitneyu(on_time, late, alternative="two-sided")
    # rank-biserial correlation: share of (on-time, late) pairs where on-time scores higher, minus the reverse
    rbc = 2 * u / (len(on_time) * len(late)) - 1

    rep = pd.read_csv(OUT / "06_repeat_purchase.csv").set_index("first_experience")
    table = [
        [rep.loc["First order late", "repeat_customers"],
         rep.loc["First order late", "customers"] - rep.loc["First order late", "repeat_customers"]],
        [rep.loc["First order on time", "repeat_customers"],
         rep.loc["First order on time", "customers"] - rep.loc["First order on time", "repeat_customers"]],
    ]
    chi2, p_chi, _, _ = stats.chi2_contingency(table)

    return {
        "reviews_mann_whitney": {
            "n_on_time": int(len(on_time)),
            "n_late": int(len(late)),
            "mean_on_time": round(float(on_time.mean()), 2),
            "mean_late": round(float(late.mean()), 2),
            "U": float(u),
            "p_value": float(p),
            "rank_biserial": round(float(rbc), 3),
        },
        "repeat_chi_square": {"chi2": round(float(chi2), 2), "p_value": float(p_chi)},
    }


def headline(con: duckdb.DuckDBPyConnection) -> dict:
    row = con.sql("""
        SELECT count(*) AS orders,
               count(DISTINCT customer_unique_id) AS customers,
               round(100.0 * avg(is_late::INT), 1) AS pct_late,
               round(avg(delivery_days), 1) AS avg_delivery_days,
               round(median(delivery_days), 0) AS median_delivery_days,
               min(purchased_at)::DATE AS first_purchase,
               max(purchased_at)::DATE AS last_purchase
        FROM fct_orders
    """).df().iloc[0]
    return {k: (v.isoformat() if hasattr(v, "isoformat") else (v.item() if hasattr(v, "item") else v))
            for k, v in row.items()}


def main() -> None:
    con = connect()
    results = run_sql(con)
    summary = {"scope": headline(con), "tests": tests(con)}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    from charts import draw_all  # local module
    draw_all(results, ROOT / "charts")

    pd.set_option("display.width", 160)
    for name, df in results.items():
        print(f"\n== {name} ==")
        print(df.head(12).to_string(index=False))
    print("\n== summary ==")
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
