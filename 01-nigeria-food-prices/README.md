# Naira on the Plate

In January 2023, a 2.5 kg bag of beans cost about **₦1,078**. By September 2024 it cost **₦4,597**. For the last two years, food prices are what everyone around me has talked about. So I went to the data to answer three things: how bad did it get, is it really getting better, and is it the same everywhere?

**The short version:**

- At the worst point, in **June 2024**, food prices were rising **112%** a year.
- Since **August 2025** they've been falling, but they're still about **2.5x** what they were in January 2023.
- The fall isn't even. Staples like rice, beans and garri are about **35%** off their peak. Meat, eggs and milk are only **4%** off theirs.
- Where you live matters. The same basic plate costs **25% more** in the South South than in the North West.

**Tools:** SQL (MySQL), Excel, Python (pandas, matplotlib)
**Data:** World Bank, [Monthly food price estimates by product and market, Nigeria](https://microdata.worldbank.org/catalog/4503). 68 markets, monthly, January 2019 to July 2026.

## What I found

### Prices more than doubled, then started to fall

![Food inflation](charts/food_inflation.png)

Food was already getting 15 to 33% more expensive every year through 2021 and 2022. Then in mid-2023 it took off. By June 2024, food cost 112% more than it had a year before.

It cooled down fast through 2025. In August 2025 the line crossed zero, which means food is now a little cheaper than it was a year earlier (4.9% cheaper in July 2026).

That's good news, but it's not the whole story. Food is still 2.52 times what it cost in January 2023. Prices coming down slowly from a very high place is not the same as food being cheap.

### Staples came back down. Protein didn't.

![Grains vs protein](charts/grains_vs_protein.png)

I split the foods into two groups and set both to 100 in January 2023:

- **Grains, beans and garri** (beans, garri, maize, maize flour, millet, rice, sorghum) peaked at 318 in September 2024. They're now back to 208.
- **Meat, eggs and milk** (beef, goat meat, eggs, milk) peaked later, at 286 in July 2025. They're still at 273.

![Fall from peak](charts/fall_from_peak.png)

Beans now cost half what they did at their peak. Maize, sorghum and millet are down 42 to 46%. Beef and goat meat are only 2 to 3% below their peak. So if you mostly buy rice and beans, things are getting easier. If you're trying to buy eggs or meat, they really aren't.

| Food | Jan 2023 | Peak | Peak month | Jul 2026 | Down from peak |
| --- | ---: | ---: | --- | ---: | ---: |
| Beans (2.5 kg) | ₦1,078 | ₦4,597 | Sep 2024 | ₦2,277 | -50% |
| Maize (1 kg) | ₦425 | ₦1,524 | Jul 2025 | ₦830 | -46% |
| Garri (1 kg) | ₦342 | ₦1,300 | Mar 2025 | ₦827 | -36% |
| Rice (1 kg) | ₦832 | ₦2,879 | Mar 2025 | ₦2,200 | -24% |
| Yam (2.5 kg) | ₦852 | ₦3,157 | Mar 2025 | ₦2,849 | -10% |
| Eggs (30) | ₦2,068 | ₦6,452 | Jul 2025 | ₦5,987 | -7% |
| Beef (1 kg) | ₦1,970 | ₦6,535 | Jul 2025 | ₦6,361 | -3% |

Every food is in [`outputs/commodity_change.csv`](outputs/commodity_change.csv).

### The south is paying more now

![Plate cost by zone](charts/plate_by_zone.png)

To compare regions with one number, I priced a simple plate: 1 kg each of rice, beans and garri. In July 2026 that plate costs ₦4,011 in the South South and ₦3,971 in the South East. In the North West it's ₦3,208. That's a 25% gap.

It wasn't always this way. At the peak in March 2025, the North West was actually the most expensive zone, at ₦5,449. Since then its prices have dropped 41%, while the South South dropped only 24%.

My guess is that most of these grains are grown in the north, so the north felt the drop first and it hasn't fully reached the south yet. But that's a guess. This data can't prove it.

| Zone | Jan 2023 | Mar 2025 (peak) | Jul 2026 |
| --- | ---: | ---: | ---: |
| South South | ₦1,611 | ₦5,300 | ₦4,011 |
| South East | ₦1,700 | ₦5,411 | ₦3,971 |
| North Central | ₦1,427 | ₦5,219 | ₦3,742 |
| South West | ₦1,491 | ₦4,817 | ₦3,717 |
| North West | ₦1,440 | ₦5,449 | ₦3,208 |

State-level numbers are in [`outputs/plate_by_state.csv`](outputs/plate_by_state.csv), but most states only have one or two markets, so I wouldn't lean on them.

## What it means

- **The worst is over, but prices aren't going back.** Food is getting cheaper slowly, starting from about 2.5x where it was in early 2023.
- **Protein is the real problem now.** Cheap calories got cheaper. Meat, eggs and milk didn't. For anyone thinking about nutrition, that matters more than the headline inflation number.
- **The south is waiting.** Prices fell faster where the food is grown. Whatever is slowing that down on the way south, like transport, storage or middlemen, is worth a closer look.

## Cleaning the data

This is the World Bank's Real-Time Food Prices data for Nigeria. It starts from market prices collected by WFP and FAO, then uses a model to fill in the months and markets where nobody collected a price. It's a tidy-looking file, but it still needed some work before I could trust it.

Here's every step, with the row count after each one. The counts come straight from [`08_cleaning_log.sql`](sql/08_cleaning_log.sql), and the table is saved in [`outputs/cleaning_log.csv`](outputs/cleaning_log.csv). One row in the file is one price series (a market, a zone or the national average) in one month.

| Step | What I did | Rows after | Why |
| ---: | --- | ---: | --- |
| 1 | Started with the raw file | 17,464 | 74 price series, 236 months (Jan 2007 to Aug 2026), 137 columns |
| 2 | Dropped August 2026 | 17,390 | The file says its last real survey was July 2026, so August is a forecast, not data |
| 3 | Kept January 2019 onward | 6,734 | Earlier years are much thinner (under 10% of prices collected before 2017). 2019 also gives four full years before the 2023 jump |
| 4 | Checked for duplicate market-months | 6,734 | Found none |
| 5 | Sorted the rows into three kinds | 6,734 | 68 real markets, 5 zone series and 1 national average. Each is used for something different |
| 6 | Fixed two mislabelled markets | 6,734 | See below |
| 7 | Checked for missing prices | 6,734 | None in the window, so nothing to fill |
| 8 | Noted how much is estimated | 6,734 | Only 24.3% of market prices since 2019 were actually collected. The rest are model estimates |
| 9 | Put prices on the same footing | 6,734 | Each food has its own unit, so for the plate cost I converted rice, beans and garri to per kg |

**The two mislabelled markets.** Two rows looked like summary rows at first: one labelled "National Average" and one labelled "Kano State (1)". My first pass set them aside. When I checked more closely, they turned out to be real markets. "National Average" is Abuja market and "Kano State (1)" is Kano city market. Each has its own map coordinates, over 200 prices that were actually collected, and a price series that doesn't copy any other row. So I renamed their states to FCT and Kano and counted them as markets. That took the market count from 66 to 68. None of the headline numbers changed, since those use the national average and zone rows, but the state table now includes Abuja and a second Kano market.

**Two more things to know:**

- **I use the model's monthly "close" price throughout.** That's how the World Bank means the data to be used, and it's why there are no gaps to fill. The catch is step 8: most of those prices are estimates.
- **Most markets are in the north-east.** 53 of the 68 are in Borno, Yobe and Adamawa, probably because a lot of this monitoring is humanitarian work. Lagos, Oyo and Abia have one market each, so I compare regions using the zone series, not single states.

## How I did it

All the analysis is in SQL, run in MySQL. Python loads the CSV into a table, runs the queries and draws the charts.

1. Clean the raw file into tables I can work with: mark which rows are real markets, work out the plate cost, count how many prices were actually collected, and turn the 16 food columns into one row per month per food ([`01_staging.sql`](sql/01_staging.sql))
2. The food price index and yearly inflation ([`02`](sql/02_national_index.sql))
3. Each food's price in January 2023, its peak and where it is now. `arg_max` finds the peak month ([`03`](sql/03_commodity_change.sql))
4. Grains vs protein, both set to 100 in January 2023 ([`04`](sql/04_group_index.sql))
5. The plate cost by zone and by state ([`05`](sql/05_plate_by_zone.sql), [`06`](sql/06_plate_by_state.sql))
6. How much of the data was really collected vs estimated, year by year ([`07`](sql/07_observed_share.sql))
7. The cleaning log above, with every step and row count ([`08`](sql/08_cleaning_log.sql))

## The Excel version

If you'd rather click around than read SQL, open [`excel/naira_on_the_plate.xlsx`](excel/naira_on_the_plate.xlsx):

- **Pick a food:** choose any food from the dropdown and watch its price since 2019
- **Peak to now:** every food's January 2023 price, its peak, and how far it has fallen
- **By zone:** the plate cost in each zone, with a chart

Only the two data sheets have typed-in numbers. Everything else is a formula (`INDEX`/`MATCH`, `MAX`, `SUMIFS`), so you can click any number and trace it back to the data. I checked every number in the workbook against the SQL results and they match.

## What this can't tell you

- About three quarters of the prices since 2019 are model estimates (see step 8 of the cleaning log). The trends are probably solid, but a single market in a single month is less certain.
- Most markets are in the north-east, so the national average leans that way.
- I didn't work out *why* prices moved. The rise lines up with the 2023 fuel subsidy removal and the naira devaluation, but this data alone can't prove one caused the other.
- The World Bank keeps updating these estimates. I used the version downloaded on 3 August 2026, so a newer download could give slightly different numbers.

## Run it yourself

1. Download the CSV from the [World Bank Microdata Library](https://microdata.worldbank.org/catalog/4503) (you'll need a free account) and put it in `data/raw/`. The file is named like `NGA_RTFP_mkt_2007_YYYY-MM-DD.csv`.
2. You need MySQL 8 running. Each project creates its own database and loads the raw data into it. If you don't log in as `root` with no password, set `MYSQL_USER` and `MYSQL_PASSWORD` first (and `MYSQL_HOST` if it isn't on your machine).
3. Then:

```bash
pip install -r requirements.txt
python src/analyze.py
python src/build_excel.py   # rebuilds the Excel workbook
```

Every number in this write-up comes from the files in [`outputs/`](outputs/).
