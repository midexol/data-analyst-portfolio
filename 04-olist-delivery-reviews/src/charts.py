"""Static charts for the README (PNG, light background, readable on GitHub)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
S1 = "#2a78d6"  # categorical slot 1
S2 = "#eb6834"  # categorical slot 2

plt.rcParams.update({
    "figure.facecolor": SURFACE,
    "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID,
    "axes.labelcolor": INK_2,
    "xtick.color": INK_2,
    "ytick.color": INK_2,
    "text.color": INK,
    "font.size": 11,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": False,
    "axes.grid": True,
    "axes.grid.axis": "y",
    "grid.color": GRID,
    "grid.linewidth": 0.8,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.axisbelow": True,
})


def _save(fig, path: Path) -> None:
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def reviews_by_delay(df: pd.DataFrame, out: Path) -> None:
    labels = [b.split(" · ")[1] for b in df.delay_bucket]
    fig, ax = plt.subplots(figsize=(8, 4.4))
    bars = ax.bar(labels, df.avg_review, color=S1, width=0.62)
    ax.set_ylim(0, 5)
    ax.set_ylabel("Average review (1-5 stars)")
    ax.set_title("Average review score by days late")
    for b, v in zip(bars, df.avg_review):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", color=INK, fontsize=11)
    ax.tick_params(axis="x", length=0)
    _save(fig, out / "reviews_by_delay.png")


def late_rate_by_month(df: pd.DataFrame, out: Path) -> None:
    df = df.copy()
    df["month"] = pd.to_datetime(df["month"])
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.plot(df.month, df.pct_late, color=S1, linewidth=2)
    ax.scatter(df.month, df.pct_late, color=S1, s=14, zorder=3)
    ax.set_ylim(0, max(df.pct_late) * 1.25)
    ax.set_ylabel("Orders delivered late (%)")
    ax.set_title("Share of orders delivered late, by month")
    labels = [("2018-03-01", (0, 9), "center", "bottom")]
    for when, offset, ha, va in labels:
        r = df[df.month == when].iloc[0]
        ax.annotate(f"{r.month:%b %Y}: {r.pct_late:.1f}%", (r.month, r.pct_late),
                    xytext=offset, textcoords="offset points", ha=ha, va=va, fontsize=10, color=INK)
    nov = df[df.month == "2017-11-01"].iloc[0]
    ax.annotate(f"Nov 2017: {nov.pct_late:.1f}%", (nov.month, nov.pct_late),
                xytext=(0, 9), textcoords="offset points", ha="center", fontsize=10, color=INK)
    _save(fig, out / "late_rate_by_month.png")


def repeat_by_first_experience(df: pd.DataFrame, out: Path) -> None:
    df = df.sort_values("first_experience", ascending=False)  # on time first
    fig, ax = plt.subplots(figsize=(6.4, 4))
    bars = ax.bar(df.first_experience, df.pct_repeat, color=S1, width=0.5)
    ax.set_ylim(0, max(df.pct_repeat) * 1.3)
    ax.set_ylabel("Customers who ordered again (%)")
    ax.set_title("Repeat purchase rate by first order delivery")
    for b, v, n in zip(bars, df.pct_repeat, df.customers):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}%\n(n = {n:,})", ha="center", fontsize=10)
    ax.tick_params(axis="x", length=0)
    _save(fig, out / "repeat_by_first_experience.png")


def late_rate_by_state(df: pd.DataFrame, out: Path) -> None:
    df = df.sort_values("pct_late")
    fig, ax = plt.subplots(figsize=(7.5, 6.2))
    ax.barh(df.customer_state, df.pct_late, color=S1, height=0.62)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("Orders delivered late (%)")
    ax.set_title("Late rate by customer state (500+ orders)")
    for y, v in enumerate(df.pct_late):
        ax.text(v + 0.25, y, f"{v:.1f}", va="center", fontsize=9, color=INK_2)
    ax.tick_params(axis="y", length=0)
    _save(fig, out / "late_rate_by_state.png")


def rfm_share(df: pd.DataFrame, out: Path) -> None:
    labels = [s.split(" · ")[1] for s in df.segment]
    y = range(len(df))
    h = 0.36
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.barh([i - h / 2 - 0.02 for i in y], df.pct_customers, height=h, color=S1, label="Share of customers")
    ax.barh([i + h / 2 + 0.02 for i in y], df.pct_revenue, height=h, color=S2, label="Share of revenue")
    ax.set_yticks(list(y), labels)
    ax.invert_yaxis()
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    ax.set_xlabel("%")
    ax.set_title("Share of customers and revenue by customer segment")
    for i, (c, r) in enumerate(zip(df.pct_customers, df.pct_revenue)):
        ax.text(c + 0.4, i - h / 2 - 0.02, f"{c:.1f}", va="center", fontsize=9, color=INK_2)
        ax.text(r + 0.4, i + h / 2 + 0.02, f"{r:.1f}", va="center", fontsize=9, color=INK_2)
    ax.legend(frameon=False, loc="upper right")
    ax.tick_params(axis="y", length=0)
    _save(fig, out / "rfm_customers_vs_revenue.png")


def draw_all(results: dict[str, pd.DataFrame], out: Path) -> None:
    out.mkdir(exist_ok=True)
    reviews_by_delay(results["02_delivery_vs_reviews"], out)
    late_rate_by_month(results["03_late_rate_by_month"], out)
    late_rate_by_state(results["04_late_rate_by_state"], out)
    repeat_by_first_experience(results["06_repeat_purchase"], out)
    rfm_share(results["07_rfm_segments"], out)
