# Naira on the Plate

In January 2023, a 2.5 kg bag of beans cost about **₦1,078**. By September 2024 it cost **₦4,597**. For the last two years, food prices are what everyone around me has talked about. So I went to the data to answer three things: how bad did it get, is it really getting better, and is it the same everywhere?

**The short version:**

- At the worst point, in **June 2024**, food prices were rising **112%** a year.
- Since **August 2025** they've been falling, but they're still about **2.5x** what they were in January 2023.
- The fall isn't even. Staples like rice, beans and garri are about **35%** off their peak. Meat, eggs and milk are only **4%** off theirs.
- Where you live matters. The same basic plate costs **25% more** in the South South than in the North West.

**Tools:** SQL (DuckDB), Excel, Python (pandas, matplotlib)
**Data:** World Bank, [Monthly food price estimates by product and market, Nigeria](https://microdata.worldbank.org/catalog/4503). 66 markets, monthly, January 2019 to July 2026.

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

## About the data

This is the World Bank's Real-Time Food Prices data for Nigeria. It starts from market prices collected by WFP and FAO, then uses a model to fill in the months and markets where nobody collected a price. A few things I had to work around:

- **Most prices are estimates.** Since 2019, only about 24% of the prices were actually collected in a market. The rest come from the World Bank's model. Before 2016 it's under 10%, which is why I start in 2019. I use the model's monthly "close" price throughout, which is how the dataset is meant to be used.
- **Some rows aren't real markets.** There's a "Market Average" row (the national series I use), five rows for the geopolitical zones, and a row called "National Average" that turned out to be just the Abuja market. I kept all of those apart from the 66 real markets.
- **Every food has its own unit.** Beans are priced per 2.5 kg, eggs per 30, milk per 400 g. For the plate cost I turned everything into a price per kg.
- **Most markets are in the north-east.** 53 of the 66 are in Borno, Yobe and Adamawa, probably because a lot of this monitoring is humanitarian work. Lagos, Oyo and Abia have one market each, so I compare regions using the zone averages, not single states.
- The file goes up to August 2026, but July 2026 is the last month with real survey data, so I stop there.

## How I did it

All the analysis is in SQL, run with DuckDB straight on the CSV. Python just runs the queries and draws the charts.

1. Clean the raw file into tables I can work with: mark which rows are real markets, work out the plate cost, count how many prices were actually collected, and turn the 16 food columns into one row per month per food ([`01_staging.sql`](sql/01_staging.sql))
2. The food price index and yearly inflation ([`02`](sql/02_national_index.sql))
3. Each food's price in January 2023, its peak and where it is now. `arg_max` finds the peak month ([`03`](sql/03_commodity_change.sql))
4. Grains vs protein, both set to 100 in January 2023 ([`04`](sql/04_group_index.sql))
5. The plate cost by zone and by state ([`05`](sql/05_plate_by_zone.sql), [`06`](sql/06_plate_by_state.sql))
6. How much of the data was really collected vs estimated, year by year ([`07`](sql/07_observed_share.sql))

## The Excel version

If you'd rather click around than read SQL, open [`excel/naira_on_the_plate.xlsx`](excel/naira_on_the_plate.xlsx):

- **Pick a food:** choose any food from the dropdown and watch its price since 2019
- **Peak to now:** every food's January 2023 price, its peak, and how far it has fallen
- **By zone:** the plate cost in each zone, with a chart

Only the two data sheets have typed-in numbers. Everything else is a formula (`INDEX`/`MATCH`, `MAX`, `SUMIFS`), so you can click any number and trace it back to the data. I checked every number in the workbook against the SQL results and they match.

## What this can't tell you

- About three quarters of the prices since 2019 are model estimates. The trends are probably solid, but a single market in a single month is less certain.
- Most markets are in the north-east, so the national average leans that way.
- I didn't work out *why* prices moved. The rise lines up with the 2023 fuel subsidy removal and the naira devaluation, but this data alone can't prove one caused the other.
- The World Bank keeps updating these estimates. I used the version downloaded on 3 August 2026, so a newer download could give slightly different numbers.

## Run it yourself

1. Download the CSV from the [World Bank Microdata Library](https://microdata.worldbank.org/catalog/4503) (you'll need a free account) and put it in `data/raw/`. The file is named like `NGA_RTFP_mkt_2007_YYYY-MM-DD.csv`.
2. Then:

```bash
pip install -r requirements.txt
python src/analyze.py
python src/build_excel.py   # rebuilds the Excel workbook
```

Every number in this write-up comes from the files in [`outputs/`](outputs/).
