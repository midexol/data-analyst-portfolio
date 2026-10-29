"""Run the full Olist delivery-vs-reviews analysis.

Usage (from the project folder):
    python src/run_analysis.py

Loads the raw CSVs in data/raw/ into MySQL, runs every file in sql/ in order,
writes each result to outputs/, runs the statistical tests, draws the charts
into charts/, and writes outputs/summary.json with the headline numbers.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy import stats

import db

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
SQL = ROOT / "sql"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

DATABASE = "olist"

# table name: (file, date columns, columns to load)
RAW_TABLES = {
    "raw_orders": ("olist_orders_dataset.csv",
                   ["order_purchase_timestamp", "order_delivered_customer_date", "order_estimated_delivery_date"],
                   ["order_id", "customer_id", "order_status", "order_purchase_timestamp",
                    "order_delivered_customer_date", "order_estimated_delivery_date"]),
    "raw_reviews": ("olist_order_reviews_dataset.csv",
                    ["review_creation_date", "review_answer_timestamp"],
                    ["review_id", "order_id", "review_score", "review_creation_date", "review_answer_timestamp"]),
    "raw_customers": ("olist_customers_dataset.csv", [],
                      ["customer_id", "customer_unique_id", "customer_state"]),
    "raw_items": ("olist_order_items_dataset.csv", [],
                  ["order_id", "seller_id", "price", "freight_value"]),
}


def connect():
    for name, (file, dates, cols) in RAW_TABLES.items():
        path = RAW / file
        if not path.exists():
            raise SystemExit(f"Missing {path}. See data/README.md for how to download the data.")
        rows = db.load_csv(DATABASE, name, path, usecols=cols, parse_dates=dates)
        print(f"loaded {rows:,} rows into {name}")
    con = db.connect(DATABASE)
    with con.cursor() as cur:  # indexes keep the joins fast
        for t, c in [("raw_orders", "order_id"), ("raw_orders", "customer_id"), ("raw_reviews", "order_id"),
                     ("raw_customers", "customer_id"), ("raw_items", "order_id")]:
            cur.execute(f"CREATE INDEX ix_{t}_{c} ON {t} ({c}(32))")
    return con


def run_sql(con) -> dict[str, pd.DataFrame]:
    results: dict[str, pd.DataFrame] = {}
    for f in sorted(SQL.glob("*.sql")):
        df = db.run_file(con, f)
        if f.name.startswith("01_"):
            continue  # staging: creates tables, returns nothing
        df.to_csv(OUT / f"{f.stem}.csv", index=False)
        results[f.stem] = df
    return results


def tests(con) -> dict:
    df = db.query(con, "SELECT is_late, review_score FROM fct_orders WHERE review_score IS NOT NULL")
    df["is_late"] = df.is_late.astype(bool)
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


def headline(con) -> dict:
    row = db.query(con, """
        WITH ordered AS (
            SELECT delivery_days, row_number() OVER (ORDER BY delivery_days) AS rn, count(*) OVER () AS n
            FROM fct_orders
        )
        SELECT count(*) AS orders,
               count(DISTINCT customer_unique_id) AS customers,
               round(100 * avg(is_late * 1e0), 1) AS pct_late,
               round(avg(delivery_days * 1e0), 1) AS avg_delivery_days,
               (SELECT round(avg(delivery_days), 0) FROM ordered
                WHERE rn IN (FLOOR((n + 1) / 2), CEIL((n + 1) / 2))) AS median_delivery_days,
               CAST(min(purchased_at) AS DATE) AS first_purchase,
               CAST(max(purchased_at) AS DATE) AS last_purchase
        FROM fct_orders
    """).iloc[0]
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
