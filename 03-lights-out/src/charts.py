"""Charts for the write-up (PNG, light background, readable on GitHub)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

SURFACE, INK, INK_2, GRID, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df", "#b8b6b0"
NG, BD = "#2a78d6", "#eb6834"  # Nigeria, Bangladesh

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


def twins(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    order = ["Ghana", "Kenya", "Ethiopia", "Bangladesh", "Nigeria"]  # coloured lines drawn last
    for country in order:
        s = df[df.country == country]
        colour = NG if country == "Nigeria" else BD if country == "Bangladesh" else MUTED
        width = 2.6 if colour != MUTED else 1.6
        ax.plot(s.year, s.kwh_per_person, color=colour, linewidth=width)
        last = s.iloc[-1]
        ax.annotate(f"{country}  {last.kwh_per_person:,.0f}", (last.year, last.kwh_per_person),
                    xytext=(6, 0), textcoords="offset points", va="center", fontsize=10,
                    color=INK if colour != MUTED else INK_2, fontweight="bold" if colour != MUTED else "normal")
    first = df[(df.year == 2000) & df.country.isin(["Nigeria", "Bangladesh"])]
    ax.annotate("2000: both at about 117 kWh", (2000, first.kwh_per_person.mean()),
                xytext=(10, 40), textcoords="offset points", fontsize=10, color=INK,
                arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8))
    ax.set_xlim(2000, 2028)
    ax.set_ylim(0, None)
    ax.set_ylabel("Grid electricity per person (kWh a year)")
    ax.set_title("Grid electricity per person, 2000 to 2024")
    _save(fig, out / "nigeria_vs_bangladesh.png")


def more_power(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.axhline(100, color=INK_2, linewidth=1, linestyle="--")
    series = [("generation_index", "Electricity made", NG), ("population_index", "People", BD),
              ("per_person_index", "Electricity per person", INK)]
    for col, label, colour in series:
        ax.plot(df.year, df[col], color=colour, linewidth=2.4)
        last = df.iloc[-1]
        ax.annotate(f"{label}  {last[col]:.0f}", (last.year, last[col]), xytext=(6, 0),
                    textcoords="offset points", va="center", fontsize=10, color=INK)
    ax.set_xlim(2000, 2030)
    ax.set_ylabel("Index (2000 = 100)")
    ax.set_title("Nigeria: power, population and power per person (2000 = 100)")
    _save(fig, out / "more_power_more_people.png")


def mix(df: pd.DataFrame, out: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.stackplot(df.year, df.gas_pct, df.hydro_pct, df.solar_pct + df.other_pct.clip(lower=0),
                 colors=[NG, "#1baf7a", "#eda100"], edgecolor=SURFACE, linewidth=1.5)
    last = df.iloc[-1]
    ax.text(2023.6, last.gas_pct / 2, f"Gas  {last.gas_pct:.0f}%", ha="right", va="center", color="white", fontsize=11, fontweight="bold")
    ax.text(2023.6, last.gas_pct + last.hydro_pct / 2, f"Hydro  {last.hydro_pct:.0f}%", ha="right", va="center", color="white", fontsize=11, fontweight="bold")
    ax.annotate(f"Solar  {last.solar_pct:.1f}%", (2024, 99.8), xytext=(-4, 14), textcoords="offset points",
                ha="right", fontsize=10, color=INK, arrowprops=dict(arrowstyle="-", color=INK_2, lw=0.8))
    ax.set_xlim(2000, 2024)
    ax.set_ylim(0, 100)
    ax.set_ylabel("Share of grid electricity (%)")
    ax.set_title("Nigeria's electricity by source")
    _save(fig, out / "power_mix.png")


def rank(df: pd.DataFrame, out: Path) -> None:
    d = df.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 5.6))
    colours = [NG if c == "Nigeria" else MUTED for c in d.country]
    ax.barh(d.country, d.kwh_per_person, color=colours, height=0.65)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", visible=True)
    for y, v in enumerate(d.kwh_per_person):
        ax.text(v + 6, y, f"{v:,.0f}", va="center", fontsize=9, color=INK_2)
    ax.set_xlabel("Grid electricity per person, 2024 (kWh)")
    ax.set_title("Lowest grid electricity per person, 2024")
    ax.tick_params(axis="y", length=0)
    _save(fig, out / "lowest_countries.png")


def draw_all(r: dict[str, pd.DataFrame], out: Path) -> None:
    out.mkdir(exist_ok=True)
    twins(r["per_person"], out)
    more_power(r["more_power_more_people"], out)
    mix(r["power_mix"], out)
    rank(r["world_rank"], out)
