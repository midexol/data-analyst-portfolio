# data-analyst-portfolio

Hi, I'm Olamide Okunola. Most people call me Mide, and online I'm midexol pretty much everywhere. I study Computer Science at FUTA in Akure, Nigeria.

Every project here uses public data, so you can rerun my work and check every number yourself.

## Projects

| Project | The question | Tools |
| --- | --- | --- |
| [Electricity in Nigeria compared with similar countries](03-lights-out/) | Why does Nigeria get so little grid power? | SQL, Python, Jupyter |
| [Food prices in Nigeria, 2019 to 2026](01-nigeria-food-prices/) | How much did food prices rise, and are they coming down? | SQL, Excel, Python |
| [How accurate Polymarket predictions are](02-polymarket-calibration/) | When Polymarket says 70%, does it happen 70% of the time? | SQL, Python |
| [How late deliveries affect reviews and repeat orders](04-olist-delivery-reviews/) | What does a late delivery cost an online store? | SQL, Python |

All the SQL runs in MySQL.

## Summaries

### Electricity in Nigeria compared with similar countries

In 2000, the average person in Nigeria and the average person in Bangladesh got about the same amount of grid electricity. By 2024, someone in Bangladesh got more than three times as much. It isn't because Nigeria is poorer: in 2022 the two countries had about the same income per person, and countries at that income usually get about four times the power Nigeria does.

![Grid electricity per person, 2000 to 2024](03-lights-out/charts/nigeria_vs_bangladesh.png)

[Read the write-up](03-lights-out/), or see the [exploration notebook](03-lights-out/notebooks/explore.ipynb).

### Food prices in Nigeria, 2019 to 2026

At the peak, in June 2024, food cost more than twice what it did a year earlier. Prices have been falling since August 2025, but they're still about 2.5 times what they were in early 2023. Rice, beans and garri are about 35% below their highest price. Meat, eggs and milk are only 4% below.

![Staples vs meat, eggs and milk](01-nigeria-food-prices/charts/grains_vs_protein.png)

[Read the write-up](01-nigeria-food-prices/), or open the [Excel workbook](01-nigeria-food-prices/excel/naira_on_the_plate.xlsx) and pick any food to see its price since 2019.

### How accurate Polymarket predictions are

I checked 1,890 settled Polymarket markets. The odds were mostly right, and got more accurate closer to the event. The exception is underdogs: bets priced at 10 to 40% came true 35% of the time, not the 23% the odds suggested.

![Market price vs how often YES happened](02-polymarket-calibration/charts/calibration.png)

[Read the write-up](02-polymarket-calibration/).

### How late deliveries affect reviews and repeat orders

Using 96,203 orders from Olist, a Brazilian online marketplace: orders that arrived on time averaged 4.28 stars out of 5, and late ones averaged 2.26. First-time buyers whose order came late were 25% less likely to order again. Just 98 of 2,945 sellers caused half of all late orders.

![Average review score by days late](04-olist-delivery-reviews/charts/reviews_by_delay.png)

[Read the write-up](04-olist-delivery-reviews/).

## How each project is laid out

- `README.md` is the write-up
- `sql/` has the queries, numbered in the order they run
- `src/` has the scripts that download the data, load it into MySQL and run everything
- `outputs/` has the result tables. Every number in a write-up comes from here
- `charts/` has the charts

Raw data isn't saved in the repo. Each project tells you where to get it.

## Contact

Email is the fastest way to reach me: okunolaolamide7@gmail.com
