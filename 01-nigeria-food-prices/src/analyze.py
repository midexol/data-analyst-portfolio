"""Nigeria food prices 2019-2026 from the World Bank's monthly market price estimates.

Put the World Bank CSV (NGA_RTFP_mkt_*.csv) in data/raw/ and run:
    python src/analyze.py

Writes result tables to outputs/, headline numbers to outputs/summary.json and
charts to charts/.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

from charts import draw_all

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

# Rows that are averages rather than real markets.
# "National Average" is actually the Abuja market series, so it's left out of both.
AGGREGATES = {"Market Average", "Geopolitical Zone", "National Average", "Kano State (1)"}
LAST_MONTH = "2026-07-01"  # last month with survey data; anything after is a nowcast
BASE_MONTH = "2023-01-01"
START = "2019-01-01"

GRAINS = ["beans", "gari_fao", "maize_fao", "maize_flour", "millet", "rice_fao", "sorghum_fao"]
PROTEIN = ["meat_beef", "meat_goat", "eggs", "milk"]

LABELS = {
    "beans": "Beans", "eggs": "Eggs (30)", "fish": "Fish", "gari_fao": "Garri", "groundnuts": "Groundnuts",
    "maize_fao": "Maize", "maize_flour": "Maize flour", "meat_beef": "Beef", "meat_goat": "Goat meat",
    "milk": "Milk", "millet": "Millet", "onions": "Onions", "rice": "Rice (local measure)",
    "rice_fao": "Rice", "sorghum_fao": "Sorghum", "yam": "Yam",
}


def load() -> pd.DataFrame:
    files = sorted(RAW.glob("NGA_RTFP_mkt_*.csv"))
    if not files:
        raise SystemExit(f"Put the World Bank NGA_RTFP_mkt_*.csv file in {RAW} (see README).")
    df = pd.read_csv(files[-1], low_memory=False).copy()
    df["date"] = pd.to_datetime(df["price_date"])
    return df[(df.date >= START) & (df.date <= LAST_MONTH)].copy()


def units(df: pd.DataFrame) -> dict[str, tuple[float, str]]:
    comp = df["components"].iloc[0]
    return {m[1]: (float(m[2]), m[3].lower()) for m in re.finditer(r"(\w+) \(([\d.]+) (\w+), Index Weight", comp)}


def foods(df: pd.DataFrame, u: dict) -> list[str]:
    return [f for f in u if f"c_{f}" in df.columns]


def national(df: pd.DataFrame) -> pd.DataFrame:
    ma = df[df.adm1_name == "Market Average"].set_index("date").sort_index()
    return ma


def index_and_inflation(ma: pd.DataFrame) -> pd.DataFrame:
    out = ma[["c_food_price_index", "inflation_food_price_index"]].rename(
        columns={"c_food_price_index": "food_price_index", "inflation_food_price_index": "yoy_inflation_pct"})
    return out.round(3).reset_index()


def commodity_change(ma: pd.DataFrame, fs: list[str]) -> pd.DataFrame:
    rows = []
    for f in fs:
        s = ma[f"c_{f}"].loc[BASE_MONTH:]
        rows.append({
            "food": LABELS.get(f, f), "column": f,
            "price_jan_2023": round(s.iloc[0]), "peak_price": round(s.max()),
            "peak_month": s.idxmax().strftime("%Y-%m"), "price_jul_2026": round(s.iloc[-1]),
            "rise_to_peak_pct": round(100 * (s.max() / s.iloc[0] - 1)),
            "peak_to_now_pct": round(100 * (s.iloc[-1] / s.max() - 1)),
            "jan_2023_to_now_pct": round(100 * (s.iloc[-1] / s.iloc[0] - 1)),
        })
    return pd.DataFrame(rows).sort_values("peak_to_now_pct").reset_index(drop=True)


def group_index(ma: pd.DataFrame) -> pd.DataFrame:
    out = {}
    for name, group in [("Grains, beans and garri", GRAINS), ("Meat, eggs and milk", PROTEIN)]:
        cols = [f"c_{f}" for f in group]
        sub = ma.loc[BASE_MONTH:, cols]
        out[name] = (sub / sub.iloc[0]).mean(axis=1) * 100
    return pd.DataFrame(out).round(1).reset_index()


def add_plate(df: pd.DataFrame, u: dict) -> pd.DataFrame:
    # 1 kg rice + 1 kg beans + 1 kg garri, in naira
    beans_kg = u["beans"][0]
    df["plate_ngn"] = df["c_rice_fao"] + df["c_beans"] / beans_kg + df["c_gari_fao"]
    return df


def plate_by_zone(df: pd.DataFrame) -> pd.DataFrame:
    z = df[df.adm1_name == "Geopolitical Zone"]
    t = z.pivot_table(index="mkt_name", columns="date", values="plate_ngn")
    keep = [pd.Timestamp(BASE_MONTH), t.loc[:, BASE_MONTH:].mean().idxmax(), pd.Timestamp(LAST_MONTH)]
    t = t[keep].round(0)
    t.columns = [f"plate_{c:%Y_%m}" for c in t.columns]
    return t.sort_values(t.columns[-1], ascending=False).reset_index().rename(columns={"mkt_name": "zone"})


def plate_by_state(df: pd.DataFrame) -> pd.DataFrame:
    m = df[(~df.adm1_name.isin(AGGREGATES)) & (df.date == LAST_MONTH)]
    return (m.groupby("adm1_name").agg(markets=("mkt_name", "nunique"), plate_ngn=("plate_ngn", "median"))
              .round(0).sort_values("plate_ngn", ascending=False).reset_index().rename(columns={"adm1_name": "state"}))


def observed_share(df_all: pd.DataFrame, fs: list[str]) -> pd.DataFrame:
    m = df_all[~df_all.adm1_name.isin(AGGREGATES)]
    obs = m[fs].notna().mean(axis=1) * 100
    return obs.groupby(m.date.dt.year).mean().round(1).rename("pct_prices_observed").rename_axis("year").reset_index()


def main() -> None:
    df = load()
    u = units(df)
    fs = foods(df, u)
    df = add_plate(df, u)
    ma = national(df)

    files = sorted(RAW.glob("NGA_RTFP_mkt_*.csv"))
    full = pd.read_csv(files[-1], low_memory=False).copy()
    full["date"] = pd.to_datetime(full["price_date"])
    full = full[full.date <= LAST_MONTH]

    results = {
        "national_index": index_and_inflation(ma),
        "commodity_change": commodity_change(ma, fs),
        "group_index": group_index(ma),
        "plate_by_zone": plate_by_zone(df),
        "plate_by_state": plate_by_state(df),
        "observed_share_by_year": observed_share(full, fs),
    }
    for name, t in results.items():
        t.to_csv(OUT / f"{name}.csv", index=False)

    ni = results["national_index"].set_index("date")
    gi = results["group_index"].set_index("date")
    pz = results["plate_by_zone"].set_index("zone")
    obs = results["observed_share_by_year"].set_index("year")
    summary = {
        "source_file": files[-1].name,
        "months": [START[:7], LAST_MONTH[:7]],
        "real_markets": int(df[~df.adm1_name.isin(AGGREGATES)].mkt_name.nunique()),
        "peak_yoy_inflation_pct": round(float(ni.yoy_inflation_pct.max()), 1),
        "peak_yoy_month": ni.yoy_inflation_pct.idxmax().strftime("%Y-%m"),
        "latest_yoy_inflation_pct": round(float(ni.yoy_inflation_pct.iloc[-1]), 1),
        "first_negative_yoy_month": ni[(ni.index > ni.yoy_inflation_pct.idxmax()) & (ni.yoy_inflation_pct < 0)].index.min().strftime("%Y-%m"),
        "index_jul_2026_vs_jan_2023": round(float(ni.food_price_index.iloc[-1] / ni.loc[BASE_MONTH, "food_price_index"]), 2),
        "grains_index_peak": float(gi.iloc[:, 0].max()), "grains_index_peak_month": gi.iloc[:, 0].idxmax().strftime("%Y-%m"),
        "grains_index_now": float(gi.iloc[-1, 0]),
        "protein_index_peak": float(gi.iloc[:, 1].max()), "protein_index_peak_month": gi.iloc[:, 1].idxmax().strftime("%Y-%m"),
        "protein_index_now": float(gi.iloc[-1, 1]),
        "plate_jul_2026_by_zone": pz.iloc[:, -1].to_dict(),
        "pct_prices_observed_2019_2026": round(float(obs.loc[2019:2026].pct_prices_observed.mean()), 1),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))

    draw_all(results, ROOT / "charts")
    print(json.dumps(summary, indent=2, default=str))
    print(results["commodity_change"].to_string(index=False))


if __name__ == "__main__":
    main()
