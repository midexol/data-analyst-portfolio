"""Run the electricity analysis.

Usage (from the project folder):
    bash src/get_data.sh        # once, downloads the data
    python src/run_analysis.py

Loads the raw file into MySQL, runs every query in sql/ in order, saves each result
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
RAW = ROOT / "data" / "raw" / "owid-energy-data.csv"
SQL = ROOT / "sql"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)


DATABASE = "lights_out"


def connect():
    if not RAW.exists():
        raise SystemExit("Missing data. Run: bash src/get_data.sh")
    rows = db.load_csv(DATABASE, "raw_energy", RAW)
    print(f"loaded {rows:,} rows into raw_energy")
    return db.connect(DATABASE)


def run_sql(con) -> dict[str, pd.DataFrame]:
    results = {}
    for f in sorted(SQL.glob("*.sql")):
        df = db.run_file(con, f)
        if f.name.startswith("01_"):
            continue  # staging: builds tables, returns nothing
        name = f.stem.split("_", 1)[1]
        df.to_csv(OUT / f"{name}.csv", index=False)
        results[name] = df
    return results


def summarise(r: dict[str, pd.DataFrame]) -> dict:
    t = r["then_and_now"].set_index("country")
    g = r["more_power_more_people"].set_index("year")
    rank = r["world_rank"]
    ng_rank = rank[rank.country == "Nigeria"].iloc[0]
    ex = r["power_sold_abroad"]
    return {
        "nigeria_kwh_2000": float(t.loc["Nigeria", "kwh_per_person_2000"]),
        "nigeria_kwh_2024": float(t.loc["Nigeria", "kwh_per_person_2024"]),
        "bangladesh_kwh_2000": float(t.loc["Bangladesh", "kwh_per_person_2000"]),
        "bangladesh_kwh_2024": float(t.loc["Bangladesh", "kwh_per_person_2024"]),
        "bangladesh_vs_nigeria_2024": round(float(t.loc["Bangladesh", "kwh_per_person_2024"] / t.loc["Nigeria", "kwh_per_person_2024"]), 1),
        "nigeria_growth_pct_per_year": float(t.loc["Nigeria", "growth_pct_per_year"]),
        "generation_index_2024": float(g.loc[2024, "generation_index"]),
        "population_index_2024": float(g.loc[2024, "population_index"]),
        "per_person_index_2024": float(g.loc[2024, "per_person_index"]),
        "nigeria_rank_from_bottom_2024": int(ng_rank.rank_from_bottom),
        "countries_ranked": int(ng_rank.countries_ranked),
        "avg_pct_exported_2016_2024": round(float(ex[ex.year >= 2016].pct_of_generation_exported.mean()), 1),
    }


def main() -> None:
    con = connect()
    results = run_sql(con)
    summary = summarise(results)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    draw_all(results, ROOT / "charts")
    print(json.dumps(summary, indent=2))
    for name, df in results.items():
        print(f"\n== {name} ==")
        print(df.head(14).to_string(index=False))


if __name__ == "__main__":
    main()
