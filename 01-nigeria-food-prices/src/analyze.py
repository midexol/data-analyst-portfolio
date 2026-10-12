"""Price indices, state comparisons and farm-to-market markups from data/prices.parquet.

Usage:
    python src/analyze.py
Writes outputs/*.csv (ready for Power BI), outputs/summary.json and charts/*.png.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
CHARTS = ROOT / "charts"
OUT.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6"]
BASKET = {"rice": ["local rice", "imported rice", "rice"], "beans": ["brown beans", "white beans", "beans"],
          "garri": ["garri", "gari"]}
INDEX_BASE = "2024-01"


def monthly(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(month=df.date.dt.to_period("M").dt.to_timestamp())
    return (df.groupby(["month", "state", "commodity", "price_type"])
              .price_ngn_per_kg.median().rename("median_price").reset_index())


def national_index(m: pd.DataFrame) -> pd.DataFrame:
    retail = m[m.price_type.str.contains("retail")]
    nat = retail.groupby(["month", "commodity"]).median_price.median().reset_index()
    base = nat[nat.month == INDEX_BASE].set_index("commodity").median_price
    nat = nat[nat.commodity.isin(base.index)]
    nat["index"] = 100 * nat.median_price / nat.commodity.map(base)
    nat["yoy_pct"] = nat.groupby("commodity").median_price.pct_change(12) * 100
    return nat


def markups(m: pd.DataFrame) -> pd.DataFrame:
    w = m.pivot_table(index=["month", "state", "commodity"], columns="price_type",
                      values="median_price").reset_index()
    cols = {c: c for c in w.columns}
    farm = next((c for c in cols if "farm" in str(c)), None)
    retail = next((c for c in cols if "retail" in str(c)), None)
    if not farm or not retail:
        return pd.DataFrame()
    w = w.dropna(subset=[farm, retail])
    w["markup_pct"] = 100 * (w[retail] - w[farm]) / w[farm]
    return (w.groupby(["state", "commodity"]).markup_pct.median().round(1)
              .rename("median_markup_pct").reset_index().sort_values("median_markup_pct", ascending=False))


def plate_cost(m: pd.DataFrame) -> pd.DataFrame:
    latest = m[m.price_type.str.contains("retail")]
    latest = latest[latest.month == latest.month.max()]
    parts = {}
    for item, names in BASKET.items():
        sub = latest[latest.commodity.isin(names)].groupby("state").median_price.median()
        parts[item] = sub
    plate = pd.DataFrame(parts).dropna()
    plate["plate_cost_ngn_per_kg_each"] = plate.sum(axis=1).round(0)
    return plate.sort_values("plate_cost_ngn_per_kg_each").reset_index()


def chart_index(nat: pd.DataFrame) -> None:
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "text.color": INK,
                         "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
                         "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False})
    top = (nat[nat.month == nat.month.max()].sort_values("index", ascending=False).commodity.head(7))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(100, color=INK_2, linewidth=1, linestyle="--")
    for colour, c in zip(SERIES, top):
        s = nat[nat.commodity == c]
        ax.plot(s.month, s["index"], color=colour, linewidth=2, label=c.title())
    ax.set_ylabel(f"Retail price index ({INDEX_BASE} = 100)")
    ax.set_title("Staple food prices in Nigeria", loc="left", fontweight="bold")
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncol=2, fontsize=9)
    fig.tight_layout()
    fig.savefig(CHARTS / "price_index.png", dpi=160)
    plt.close(fig)


def main() -> None:
    prices = pd.read_parquet(ROOT / "data" / "prices.parquet")
    m = monthly(prices)
    m.to_csv(OUT / "monthly_state_prices.csv", index=False)

    nat = national_index(m)
    nat.to_csv(OUT / "national_index.csv", index=False)
    mk = markups(m)
    if len(mk):
        mk.to_csv(OUT / "farm_to_retail_markup.csv", index=False)
    plate = plate_cost(m)
    plate.to_csv(OUT / "plate_cost_by_state.csv", index=False)
    chart_index(nat)

    last = nat[nat.month == nat.month.max()].sort_values("yoy_pct", ascending=False)
    summary = {
        "rows": int(len(prices)),
        "date_range": [str(prices.date.min().date()), str(prices.date.max().date())],
        "latest_month": str(nat.month.max().date()),
        "fastest_rising_yoy": last[["commodity", "yoy_pct"]].dropna().head(3).round(1).to_dict("records"),
        "highest_markup": mk.head(3).to_dict("records") if len(mk) else "no farmgate prices in data",
        "plate_cost_cheapest": plate.head(1).to_dict("records"),
        "plate_cost_dearest": plate.tail(1).to_dict("records"),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
