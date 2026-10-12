"""Calibration and Brier scores from data/markets.parquet (built by fetch.py).

Usage:
    python src/analyze.py
Writes outputs/*.csv, outputs/summary.json and charts/*.png.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
CHARTS = ROOT / "charts"
OUT.mkdir(exist_ok=True)
CHARTS.mkdir(exist_ok=True)

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
SERIES = {30: "#2a78d6", 7: "#eb6834", 1: "#1baf7a"}  # categorical slots 1-3
BINS = np.linspace(0, 1, 11)


def brier(df: pd.DataFrame) -> float:
    return float(((df.price_yes - df.outcome_yes) ** 2).mean())


def calibration_table(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["bin"] = pd.cut(d.price_yes, BINS, include_lowest=True)
    t = (d.groupby(["horizon_days", "bin"], observed=True)
           .agg(markets=("outcome_yes", "size"),
                mean_forecast=("price_yes", "mean"),
                observed_rate=("outcome_yes", "mean"))
           .reset_index())
    # 95% Wilson interval on the observed rate
    n, p, z = t.markets, t.observed_rate, 1.96
    centre = (p + z**2 / (2 * n)) / (1 + z**2 / n)
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    t["ci_low"], t["ci_high"] = centre - half, centre + half
    t["bin"] = t["bin"].astype(str)
    return t


def chart(t: pd.DataFrame) -> None:
    plt.rcParams.update({"figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "text.color": INK,
                         "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2,
                         "axes.edgecolor": GRID, "axes.spines.top": False, "axes.spines.right": False})
    fig, ax = plt.subplots(figsize=(6.4, 6.2))
    ax.plot([0, 1], [0, 1], color=INK_2, linestyle="--", linewidth=1, label="Perfect calibration")
    for h, colour in SERIES.items():
        s = t[(t.horizon_days == h) & (t.markets >= 10)]
        ax.errorbar(s.mean_forecast, s.observed_rate,
                    yerr=[s.observed_rate - s.ci_low, s.ci_high - s.observed_rate],
                    color=colour, marker="o", markersize=6, linewidth=2, capsize=2,
                    label=f"{h} day{'s' if h > 1 else ''} before resolution")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Market price of YES (forecast probability)")
    ax.set_ylabel("Share that resolved YES")
    ax.set_title("Polymarket calibration", loc="left", fontweight="bold")
    ax.grid(color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout()
    fig.savefig(CHARTS / "calibration.png", dpi=160)
    plt.close(fig)


def main() -> None:
    df = pd.read_parquet(ROOT / "data" / "markets.parquet")

    t = calibration_table(df)
    t.to_csv(OUT / "calibration_bins.csv", index=False)

    by_h = df.groupby("horizon_days").apply(brier, include_groups=False).rename("brier").reset_index()
    by_cat = (df.groupby(["category", "horizon_days"]).apply(brier, include_groups=False)
                .rename("brier").reset_index())
    by_h.to_csv(OUT / "brier_by_horizon.csv", index=False)
    by_cat.to_csv(OUT / "brier_by_category.csv", index=False)

    vol_median = df.drop_duplicates("market_id").volume.median()
    df["liquidity_group"] = np.where(df.volume >= vol_median, "Above-median volume", "Below-median volume")
    by_liq = (df.groupby(["liquidity_group", "horizon_days"]).apply(brier, include_groups=False)
                .rename("brier").reset_index())
    by_liq.to_csv(OUT / "brier_by_volume.csv", index=False)

    chart(t)

    summary = {
        "markets": int(df.market_id.nunique()),
        "rows": int(len(df)),
        "share_resolved_yes": round(float(df.drop_duplicates("market_id").outcome_yes.mean()), 3),
        "brier_by_horizon": {int(r.horizon_days): round(r.brier, 4) for r in by_h.itertuples()},
        "baseline_brier_always_50pct": 0.25,
        "median_volume_usd": float(vol_median),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(by_cat.pivot(index="category", columns="horizon_days", values="brier").round(4))


if __name__ == "__main__":
    main()
