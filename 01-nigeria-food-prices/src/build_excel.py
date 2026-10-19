"""Build the Excel version of Naira on the Plate.

Usage (from the project folder, after putting the World Bank CSV in data/raw/):
    python src/build_excel.py

Writes excel/naira_on_the_plate.xlsx. The two data sheets hold the prices; every
other number in the workbook is an Excel formula, so it updates if the data changes.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.worksheet.table import Table, TableStyleInfo

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "excel"
OUT.mkdir(exist_ok=True)

START, END, BASE, PEAK_ZONE_MONTH = "2019-01-01", "2026-07-01", "2023-01-01", "2025-03-01"

# column in the World Bank file -> name shown in the workbook (unit included)
FOODS = [
    ("beans", "Beans (2.5 kg)"), ("maize_fao", "Maize (1 kg)"), ("sorghum_fao", "Sorghum (1 kg)"),
    ("millet", "Millet (2.6 kg)"), ("gari_fao", "Garri (1 kg)"), ("maize_flour", "Maize flour (2.1 kg)"),
    ("fish", "Fish (1 kg)"), ("rice_fao", "Rice (1 kg)"), ("groundnuts", "Groundnuts (2.2 kg)"),
    ("onions", "Onions (0.5 kg)"), ("yam", "Yam (2.5 kg)"), ("milk", "Milk (400 g)"),
    ("eggs", "Eggs (30)"), ("meat_beef", "Beef (1 kg)"), ("meat_goat", "Goat meat (1 kg)"),
]

FONT = "Arial"
INK, MUTED, ACCENT = "1B1C1E", "6B6E73", "2A78D6"
HEAD_FILL = PatternFill("solid", fgColor="EEF2F7")
INPUT_FILL = PatternFill("solid", fgColor="FFF2CC")
THIN = Side(style="thin", color="D9DCE1")


def f(size=10, bold=False, color=INK, italic=False):
    return Font(name=FONT, size=size, bold=bold, color=color, italic=italic)


def load() -> pd.DataFrame:
    files = sorted(RAW.glob("NGA_RTFP_mkt_*.csv"))
    if not files:
        raise SystemExit(f"Put the World Bank NGA_RTFP_mkt_*.csv file in {RAW} (see README).")
    df = pd.read_csv(files[-1], low_memory=False).copy()
    df["date"] = pd.to_datetime(df["price_date"])
    return df[(df.date >= START) & (df.date <= END)].copy(), files[-1].name


def header_row(ws, row, labels, widths=None):
    for c, label in enumerate(labels, 1):
        cell = ws.cell(row=row, column=c, value=label)
        cell.font = f(bold=True)
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="left" if c == 1 else "right", vertical="center", wrap_text=True)
        cell.border = Border(bottom=THIN)
    if widths:
        for c, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(c)].width = w


def base_sheet(ws):
    ws.sheet_view.showGridLines = False


def build(df: pd.DataFrame, source: str) -> Path:
    wb = Workbook()

    # ---------------- Prices: national average, one row per month ----------------
    nat = df[df.adm1_name == "Market Average"].sort_values("date")
    ws_p = wb.active
    ws_p.title = "Prices"
    base_sheet(ws_p)
    header_row(ws_p, 1, ["Month"] + [name for _, name in FOODS], [12] + [14] * len(FOODS))
    for r, row in enumerate(nat.itertuples(index=False), 2):
        ws_p.cell(row=r, column=1, value=row.date.to_pydatetime()).number_format = "mmm yyyy"
        for c, (key, _) in enumerate(FOODS, 2):
            cell = ws_p.cell(row=r, column=c, value=round(float(getattr(row, f"c_{key}")), 2))
            cell.number_format = "#,##0"
    last_p = 1 + len(nat)
    ws_p.freeze_panes = "B2"
    t = Table(displayName="tblPrices", ref=f"A1:{get_column_letter(1 + len(FOODS))}{last_p}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_p.add_table(t)
    for row in ws_p.iter_rows(min_row=2, max_row=last_p):
        for cell in row:
            cell.font = f()
    note = ws_p.cell(row=last_p + 2, column=1, value=f"Naira, national average across markets. Source: World Bank, Monthly food price estimates by product and market, Nigeria ({source}). Monthly estimated (close) prices.")
    note.font = f(9, color=MUTED, italic=True)

    # rows for Jan 2023 and Jul 2026 inside Prices
    dates = list(nat.date)
    r_base = 2 + dates.index(pd.Timestamp(BASE))
    r_end = 2 + dates.index(pd.Timestamp(END))
    last_col = get_column_letter(1 + len(FOODS))
    since = f"Prices!$B${r_base}:${last_col}${r_end}"
    since_dates = f"Prices!$A${r_base}:$A${r_end}"
    head = f"Prices!$B$1:${last_col}$1"

    # ---------------- Zones: plate cost by geopolitical zone ----------------
    z = df[df.adm1_name == "Geopolitical Zone"].sort_values(["date", "mkt_name"])
    ws_z = wb.create_sheet("Zones")
    base_sheet(ws_z)
    header_row(ws_z, 1, ["Month", "Zone", "Rice (1 kg)", "Beans (2.5 kg)", "Garri (1 kg)", "Plate cost"], [12, 16, 13, 14, 13, 13])
    for r, row in enumerate(z.itertuples(index=False), 2):
        ws_z.cell(row=r, column=1, value=row.date.to_pydatetime()).number_format = "mmm yyyy"
        ws_z.cell(row=r, column=2, value=row.mkt_name)
        ws_z.cell(row=r, column=3, value=round(float(row.c_rice_fao), 2)).number_format = "#,##0"
        ws_z.cell(row=r, column=4, value=round(float(row.c_beans), 2)).number_format = "#,##0"
        ws_z.cell(row=r, column=5, value=round(float(row.c_gari_fao), 2)).number_format = "#,##0"
        # 1 kg each: beans are priced per 2.5 kg
        ws_z.cell(row=r, column=6, value=f"=C{r}+D{r}/2.5+E{r}").number_format = "#,##0"
        for c in range(1, 7):
            ws_z.cell(row=r, column=c).font = f()
    last_z = 1 + len(z)
    ws_z.freeze_panes = "A2"
    tz = Table(displayName="tblZones", ref=f"A1:F{last_z}")
    tz.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
    ws_z.add_table(tz)
    n = ws_z.cell(row=last_z + 2, column=1, value="Plate cost = 1 kg rice + 1 kg beans + 1 kg garri, in naira. Beans are priced per 2.5 kg, so they're divided by 2.5. Same source as the Prices sheet.")
    n.font = f(9, color=MUTED, italic=True)

    # ---------------- Peak to now: one row per food, all formulas ----------------
    ws_s = wb.create_sheet("Peak to now", 0)
    base_sheet(ws_s)
    ws_s["A1"] = "How far has each food fallen from its peak?"
    ws_s["A1"].font = f(14, bold=True)
    ws_s["A2"] = "National average prices in naira. Peak = highest month from Jan 2023 to Jul 2026. Every number below is a formula on the Prices sheet."
    ws_s["A2"].font = f(9, color=MUTED, italic=True)
    hdr = ["Food", "Jan 2023", "Peak", "Peak month", "Jul 2026", "Rise to peak", "Down from peak", "Jan 2023 to now"]
    header_row(ws_s, 4, hdr, [22, 12, 12, 13, 12, 13, 15, 16])
    ws_s.row_dimensions[4].height = 30
    for i, (_, name) in enumerate(FOODS):
        r = 5 + i
        col = f"INDEX({since},0,MATCH($A{r},{head},0))"
        ws_s.cell(row=r, column=1, value=name)
        ws_s.cell(row=r, column=2, value=f"=INDEX({since},1,MATCH($A{r},{head},0))")
        ws_s.cell(row=r, column=3, value=f"=MAX({col})")
        ws_s.cell(row=r, column=4, value=f"=INDEX({since_dates},MATCH(C{r},{col},0))")
        ws_s.cell(row=r, column=5, value=f"=INDEX({since},ROWS({since_dates}),MATCH($A{r},{head},0))")
        ws_s.cell(row=r, column=6, value=f"=C{r}/B{r}-1")
        ws_s.cell(row=r, column=7, value=f"=E{r}/C{r}-1")
        ws_s.cell(row=r, column=8, value=f"=E{r}/B{r}-1")
        for c, fmt in zip(range(1, 9), [None, "#,##0", "#,##0", "mmm yyyy", "#,##0", "0%", "0%", "0%"]):
            cell = ws_s.cell(row=r, column=c)
            cell.font = f()
            cell.border = Border(bottom=THIN)
            if fmt:
                cell.number_format = fmt
                cell.alignment = Alignment(horizontal="right")
    last_s = 4 + len(FOODS)
    # greener = fell further from its peak, white = barely moved
    ws_s.conditional_formatting.add(f"G5:G{last_s}", ColorScaleRule(start_type="min", start_color="63BE7B", end_type="max", end_color="FFFFFF"))
    ws_s.freeze_panes = "B5"

    # ---------------- Zone summary ----------------
    ws_zs = wb.create_sheet("By zone", 1)
    base_sheet(ws_zs)
    ws_zs["A1"] = "Where does a basic plate cost the most?"
    ws_zs["A1"].font = f(14, bold=True)
    ws_zs["A2"] = "1 kg each of rice, beans and garri, in naira. Formulas pull from the Zones sheet."
    ws_zs["A2"].font = f(9, color=MUTED, italic=True)
    header_row(ws_zs, 4, ["Zone", "Jan 2023", "Mar 2025 (peak)", "Jul 2026", "Fall since peak", "vs North West now"], [18, 12, 15, 12, 14, 18])
    ws_zs.row_dimensions[4].height = 30
    # date headers as real dates in a hidden helper row so the formulas stay readable
    for c, d in zip([2, 3, 4], [BASE, PEAK_ZONE_MONTH, END]):
        ws_zs.cell(row=3, column=c, value=pd.Timestamp(d).to_pydatetime()).number_format = "mmm yyyy"
        ws_zs.cell(row=3, column=c).font = f(8, color="FFFFFF")
    zones = (z[z.date == END].assign(plate=lambda d: d.c_rice_fao + d.c_beans / 2.5 + d.c_gari_fao)
               .sort_values("plate", ascending=False).mkt_name.tolist())
    nw_row = 5 + zones.index("North West")
    for i, zone in enumerate(zones):
        r = 5 + i
        ws_zs.cell(row=r, column=1, value=zone)
        for c in (2, 3, 4):
            L = get_column_letter(c)
            ws_zs.cell(row=r, column=c, value=f"=SUMIFS(Zones!$F:$F,Zones!$A:$A,{L}$3,Zones!$B:$B,$A{r})")
        ws_zs.cell(row=r, column=5, value=f"=D{r}/C{r}-1")
        ws_zs.cell(row=r, column=6, value=f"=D{r}/$D${nw_row}-1")
        for c, fmt in zip(range(1, 7), [None, "#,##0", "#,##0", "#,##0", "0%", "0%"]):
            cell = ws_zs.cell(row=r, column=c)
            cell.font = f()
            cell.border = Border(bottom=THIN)
            if fmt:
                cell.number_format = fmt
                cell.alignment = Alignment(horizontal="right")
    last_zs = 4 + len(zones)
    ch = BarChart()
    ch.type = "bar"
    ch.title = "Plate cost by zone, Jul 2026 (naira)"
    ch.style = 10
    ch.y_axis.title = None
    ch.x_axis.title = None
    ch.legend = None
    ch.add_data(Reference(ws_zs, min_col=4, min_row=4, max_row=last_zs), titles_from_data=True)
    ch.set_categories(Reference(ws_zs, min_col=1, min_row=5, max_row=last_zs))
    ch.series[0].graphicalProperties.solidFill = ACCENT
    ch.series[0].graphicalProperties.line.solidFill = ACCENT
    ch.x_axis.scaling.orientation = "maxMin"
    ch.y_axis.crosses = "max"
    ch.y_axis.number_format = "#,##0"
    ch.x_axis.delete = False
    ch.y_axis.delete = False
    ch.height, ch.width = 7.5, 16
    ws_zs.add_chart(ch, f"A{last_zs + 3}")

    # ---------------- Food picker: dropdown + chart ----------------
    ws_f = wb.create_sheet("Pick a food", 0)
    base_sheet(ws_f)
    ws_f["A1"] = "Pick a food to see its price since 2019"
    ws_f["A1"].font = f(14, bold=True)
    ws_f["A3"] = "Food"
    ws_f["A3"].font = f(bold=True)
    ws_f["B3"] = "Beans (2.5 kg)"
    ws_f["B3"].font = f(bold=True, color=ACCENT)
    ws_f["B3"].fill = INPUT_FILL
    ws_f["C3"] = "Change this cell (dropdown)"
    ws_f["C3"].font = f(9, color=MUTED, italic=True)
    dv = DataValidation(type="list", formula1=f"='Peak to now'!$A$5:$A${last_s}", allow_blank=False)
    dv.error, dv.errorTitle = "Pick a food from the list.", "Not on the list"
    ws_f.add_data_validation(dv)
    dv.add("B3")
    stats = [("Jan 2023", "B", "#,##0"), ("Peak", "C", "#,##0"), ("Peak month", "D", "mmm yyyy"),
             ("Jul 2026", "E", "#,##0"), ("Down from peak", "G", "0%"), ("Jan 2023 to now", "H", "0%")]
    for i, (label, src, fmt) in enumerate(stats):
        r = 5 + i
        ws_f.cell(row=r, column=1, value=label).font = f(color=MUTED)
        c = ws_f.cell(row=r, column=2, value=f"=INDEX('Peak to now'!${src}$5:${src}${last_s},MATCH($B$3,'Peak to now'!$A$5:$A${last_s},0))")
        c.number_format, c.font = fmt, f(bold=True)
        c.alignment = Alignment(horizontal="right")
    # helper series the chart reads (follows the dropdown)
    hr = 13
    header_row(ws_f, hr, ["Month", "Price (naira)", "Index (Jan 2023 = 100)", "Year label"])
    for i in range(len(dates)):
        r = hr + 1 + i
        pr = 2 + i
        ws_f.cell(row=r, column=1, value=f"=Prices!A{pr}").number_format = "mmm yyyy"
        ws_f.cell(row=r, column=2, value=f"=INDEX(Prices!$B${pr}:${last_col}${pr},MATCH($B$3,{head},0))").number_format = "#,##0"
        ws_f.cell(row=r, column=3, value=f"=B{r}/$B$5*100").number_format = "0"
        # chart label: the year in January, blank otherwise
        ws_f.cell(row=r, column=4, value=f'=IF(MONTH(A{r})=1,YEAR(A{r}),"")')
        for c in (1, 2, 3, 4):
            ws_f.cell(row=r, column=c).font = f(9, color=MUTED)
    last_f = hr + len(dates)
    ws_f.column_dimensions["A"].width = 16
    ws_f.column_dimensions["B"].width = 18
    ws_f.column_dimensions["C"].width = 22
    ws_f.column_dimensions["D"].width = 11
    lc = LineChart()
    lc.title = "Monthly price, national average (naira)"
    lc.style = 10
    lc.legend = None
    lc.add_data(Reference(ws_f, min_col=2, min_row=hr, max_row=last_f), titles_from_data=True)
    lc.set_categories(Reference(ws_f, min_col=4, min_row=hr + 1, max_row=last_f))
    lc.series[0].graphicalProperties.line.solidFill = ACCENT
    lc.series[0].graphicalProperties.line.width = 22000
    lc.series[0].smooth = False
    lc.x_axis.tickLblSkip = 1
    lc.x_axis.tickMarkSkip = 12
    lc.y_axis.number_format = "#,##0"
    lc.x_axis.delete = False
    lc.y_axis.delete = False
    lc.height, lc.width = 9, 18
    ws_f.add_chart(lc, "F3")

    # ---------------- Read me ----------------
    ws_r = wb.create_sheet("Read me", 0)
    base_sheet(ws_r)
    ws_r.column_dimensions["A"].width = 22
    ws_r.column_dimensions["B"].width = 90
    rows = [
        ("Naira on the Plate", None),
        ("Nigerian food prices, Jan 2019 to Jul 2026, national average across 66 markets.", None),
        (None, None),
        ("Sheet", "What it shows"),
        ("Pick a food", "Choose any food in the yellow cell. The stats and chart update to show its price since 2019."),
        ("Peak to now", "Each food's price in Jan 2023, its peak, and how far it has fallen since. Green = fell the most."),
        ("By zone", "Cost of 1 kg each of rice, beans and garri in the five geopolitical zones, with a chart."),
        ("Prices", "The data: monthly national average price for 15 foods (in each food's own unit)."),
        ("Zones", "The data: monthly rice, beans and garri prices for each zone, plus the plate cost formula."),
        (None, None),
        ("Source", f"World Bank, Monthly food price estimates by product and market, Nigeria. File: {source}. https://microdata.worldbank.org/catalog/4503"),
        ("About the prices", "These are the World Bank's monthly estimated (close) prices. Since 2019 only about a quarter were directly collected. The rest are model estimates."),
        ("Formulas", "Only the Prices and Zones sheets contain typed-in data. Every other number is a formula, so you can trace it with Formulas > Trace Precedents."),
        ("Full analysis", "SQL, charts and write-up: github.com/midexol/data-analyst-portfolio (01-nigeria-food-prices)"),
    ]
    for r, (a, b) in enumerate(rows, 1):
        if a is not None:
            ws_r.cell(row=r, column=1, value=a)
        if b is not None:
            ws_r.cell(row=r, column=2, value=b)
        ws_r.cell(row=r, column=1).font = f()
        ws_r.cell(row=r, column=2).font = f()
        ws_r.cell(row=r, column=2).alignment = Alignment(wrap_text=True, vertical="top")
        ws_r.cell(row=r, column=1).alignment = Alignment(vertical="top")
    ws_r["A1"].font = f(16, bold=True)
    ws_r["A2"].font = f(10, color=MUTED)
    for c in ("A4", "B4"):
        ws_r[c].font = f(bold=True)
        ws_r[c].fill = HEAD_FILL
    for r in range(5, 10):
        ws_r.cell(row=r, column=1).font = f(bold=True, color=ACCENT)
    for r in range(11, 15):
        ws_r.cell(row=r, column=1).font = f(bold=True)

    for ws in wb.worksheets:
        ws.page_setup.orientation = "landscape"
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
    wb.active = 0
    path = OUT / "naira_on_the_plate.xlsx"
    wb.save(path)
    return path


if __name__ == "__main__":
    data, src = load()
    print(build(data, src))
