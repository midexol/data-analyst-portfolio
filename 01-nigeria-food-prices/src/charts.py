"""Charts for the README (PNG, light background)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE, INK, INK_2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
S1, S2 = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2, "text.color": INK,
    "font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "axes.grid.axis": "y", "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.axisbelow": True,
})


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def inflation(ni: pd.DataFrame, out: Path) -> None:
    ni = ni.copy()
    ni["date"] = pd.to_datetime(ni["date"])
    fig, ax = plt.subplots(figsize=(9, 4.4))
    ax.axhline(0, color=INK_2, linewidth=1)
    ax.plot(ni.date, ni.yoy_inflation_pct, color=S1, linewidth=2)
    peak = ni.loc[ni.yoy_inflation_pct.idxmax()]
    ax.scatter([peak.date], [peak.yoy_inflation_pct], color=S1, s=30, zorder=3)
    ax.annotate(f"{peak.date:%b %Y}: {peak.yoy_inflation_pct:.0f}%", (peak.date, peak.yoy_inflation_pct),
                xytext=(10, 0), textcoords="offset points", va="center", fontsize=10)
    ax.set_ylabel("Food prices vs a year earlier (%)")
    ax.set_title("Food inflation peaked above 100% in mid-2024")
    _save(fig, out / "food_inflation.png")


def grains_vs_protein(gi: pd.DataFrame, out: Path) -> None:
    gi = gi.copy()
    gi["date"] = pd.to_datetime(gi["date"])
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.axhline(100, color=INK_2, linewidth=1, linestyle="--")
    for col, colour in zip(gi.columns[1:], [S1, S2]):
        ax.plot(gi.date, gi[col], color=colour, linewidth=2, label=col)
        ax.annotate(f"{gi[col].iloc[-1]:.0f}", (gi.date.iloc[-1], gi[col].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=10, color=INK)
    ax.set_ylabel("Price index (Jan 2023 = 100)")
    ax.set_title("Staples came back down. Meat, eggs and milk didn't")
    ax.legend(frameon=False, loc="upper left")
    _save(fig, out / "grains_vs_protein.png")


def peak_to_now(cc: pd.DataFrame, out: Path) -> None:
    cc = cc[cc.column != "rice"].sort_values("peak_to_now_pct", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(cc.food, cc.peak_to_now_pct, color=S1, height=0.62)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.axvline(0, color=INK_2, linewidth=1)
    for y, v in enumerate(cc.peak_to_now_pct):
        ax.text(v - 1, y, f"{v}%", va="center", ha="right", fontsize=9, color=INK_2)
    ax.set_xlim(min(cc.peak_to_now_pct) - 10, 2)
    ax.set_xlabel("July 2026 price vs its peak since Jan 2023 (%)")
    ax.set_title("How far each food has fallen from its peak")
    ax.tick_params(axis="y", length=0)
    _save(fig, out / "fall_from_peak.png")


def plate_by_zone(pz: pd.DataFrame, out: Path) -> None:
    col = pz.columns[-1]
    pz = pz.sort_values(col)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.barh(pz.zone, pz[col], color=S1, height=0.6)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    for y, v in enumerate(pz[col]):
        ax.text(v + 40, y, f"₦{v:,.0f}", va="center", fontsize=10, color=INK)
    ax.set_xlim(0, pz[col].max() * 1.18)
    ax.set_xlabel("Naira for 1 kg each of rice, beans and garri (July 2026)")
    ax.set_title("The same plate costs 25% more in the South South than the North West")
    ax.tick_params(axis="y", length=0)
    _save(fig, out / "plate_by_zone.png")


def draw_all(results: dict[str, pd.DataFrame], out: Path) -> None:
    out.mkdir(exist_ok=True)
    inflation(results["national_index"], out)
    grains_vs_protein(results["group_index"], out)
    peak_to_now(results["commodity_change"], out)
    plate_by_zone(results["plate_by_zone"], out)
