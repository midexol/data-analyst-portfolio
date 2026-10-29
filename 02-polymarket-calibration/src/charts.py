"""Charts for the write-up (PNG, light background, readable on GitHub)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE, INK, INK_2, GRID, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#b8b6b0"
BLUE, ORANGE = "#2a78d6", "#eb6834"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2, "xtick.color": INK_2, "ytick.color": INK_2, "text.color": INK,
    "font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.titlesize": 14, "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.axisbelow": True,
})


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def calibration(df: pd.DataFrame, out: Path) -> None:
    s = df[df.horizon_days == 1]
    fig, ax = plt.subplots(figsize=(7, 6.4))
    ax.plot([0, 100], [0, 100], color=INK_2, linestyle="--", linewidth=1)
    ax.annotate("If the price were\nexactly right", (52, 52), xytext=(66, 34), color=INK_2, fontsize=9,
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8))
    ax.axvspan(10, 40, color=ORANGE, alpha=0.07, linewidth=0)
    ax.text(25, 4, "Underdogs", color=ORANGE, fontsize=10, ha="center", fontweight="bold")
    ax.errorbar(s.avg_price_pct, s.happened_pct,
                yerr=[s.happened_pct - s.low_pct, s.high_pct - s.happened_pct],
                color=BLUE, marker="o", markersize=7, linewidth=2, capsize=3, elinewidth=1)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Price of YES one day before the end (%)")
    ax.set_ylabel("How often YES actually happened (%)")
    ax.set_title("Market price vs how often YES happened, 1 day before")
    _save(fig, out / "calibration.png")


def underdogs(df: pd.DataFrame, out: Path) -> None:
    d = df.copy()
    d["label"] = d.price_group.str.split(". ", n=1).str[1]
    x = range(len(d))
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    ax.bar([i - 0.2 for i in x], d.avg_price_pct, width=0.38, color=MUTED, label="What the price said")
    ax.bar([i + 0.2 for i in x], d.happened_pct, width=0.38, color=BLUE, label="What actually happened")
    for i, r in enumerate(d.itertuples()):
        ax.text(i + 0.2, r.happened_pct + 1.5, f"{r.happened_pct:.0f}%", ha="center", fontsize=10,
                color=ORANGE if r.gap_pts > 5 else INK, fontweight="bold" if r.gap_pts > 5 else "normal")
    ax.set_xticks(list(x), d.label)
    ax.set_xlabel("Price of YES")
    ax.set_ylabel("%")
    ax.set_ylim(0, 108)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Price vs actual result, by price range")
    _save(fig, out / "underdogs.png")


def closer(df: pd.DataFrame, out: Path) -> None:
    d = df.sort_values("horizon_days", ascending=False)
    labels = [f"{h} day{'s' if h > 1 else ''} before" for h in d.horizon_days]
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    bars = ax.bar(labels, d.brier, color=[MUTED, MUTED, BLUE], width=0.55)
    for b, v in zip(bars, d.brier):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.002, f"{v:.3f}", ha="center", fontsize=11)
    ax.set_ylim(0, d.brier.max() * 1.18)
    ax.set_ylabel("Brier score (lower is better)")
    ax.grid(axis="x", visible=False)
    ax.set_title(f"Brier score by days before the end ({int(d.markets.iloc[0]):,} markets)")
    _save(fig, out / "closer_is_sharper.png")


def topics(df: pd.DataFrame, out: Path) -> None:
    d = df.sort_values("brier_unsure_markets", ascending=False)
    fig, ax = plt.subplots(figsize=(8, 3.8))
    colours = [BLUE if c == "economy" else MUTED for c in d.category]
    bars = ax.barh(d.category.str.capitalize(), d.brier_unsure_markets, color=colours, height=0.55)
    for b, v in zip(bars, d.brier_unsure_markets):
        ax.text(v + 0.003, b.get_y() + b.get_height() / 2, f"{v:.3f}", va="center", fontsize=10)
    ax.axvline(0.25, color=INK_2, linestyle="--", linewidth=1)
    ax.set_xlim(0, 0.28)
    ax.set_xlabel("Brier score on the close calls, one day before (lower is better).\nThe dashed line is what you'd score by always saying 50%.")
    ax.grid(axis="y", visible=False)
    ax.set_title("Brier score by topic, close calls only")
    _save(fig, out / "by_topic.png")


def draw_all(r: dict[str, pd.DataFrame], out: Path) -> None:
    out.mkdir(exist_ok=True)
    calibration(r["calibration"], out)
    underdogs(r["underdogs"], out)
    closer(r["score_by_horizon"], out)
    topics(r["score_by_topic"], out)
