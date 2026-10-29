# data-analyst-portfolio

Hi, I'm Olamide Okunola. Most people call me Mide, and online I'm midexol pretty much everywhere. I study Computer Science at FUTA in Akure, Nigeria.

Every project here uses public data, so you can rerun my work and check every number yourself.

## Projects

| Project | The question | Tools |
| --- | --- | --- |
| [Lights Out](03-lights-out/) | Why does Nigeria have so little grid power? | SQL, Python, Jupyter |
| [Naira on the Plate](01-nigeria-food-prices/) | Is food in Nigeria really getting cheaper? | SQL, Excel, Python |
| [Do Prediction Markets Know?](02-polymarket-calibration/) | When Polymarket says 70%, does it happen? | SQL, Python |
| [Late Parcels, Low Stars](04-olist-delivery-reviews/) | What does a late parcel cost a store? | SQL, Python |

All the SQL runs in MySQL.

## In short

### Lights Out

In 2000, Nigeria and Bangladesh both made about 117 kWh of grid power per person. By 2024, Bangladesh made 586 and Nigeria made 161. In 2022 the two had about the same income per person, so being poorer doesn't explain the gap. Countries at that income make about 620 kWh per person. Nigeria makes about a quarter of that.

![Grid electricity per person, 2000 to 2024](03-lights-out/charts/nigeria_vs_bangladesh.png)

[Read the full write-up](03-lights-out/), or see the [exploration notebook](03-lights-out/notebooks/explore.ipynb).

### Do Prediction Markets Know?

I scored 1,890 settled Polymarket markets. The prices were mostly right, and got sharper close to the end. The exception is underdogs: bets priced at 10 to 40% came true 35% of the time, not the 23% the price suggested.

![Market price vs how often YES happened](02-polymarket-calibration/charts/calibration.png)

[Read the full write-up](02-polymarket-calibration/).

### Naira on the Plate

In January 2023, a 2.5 kg bag of beans cost about ₦1,078. By September 2024 it was ₦4,597. I used the World Bank's price data for 68 Nigerian markets to see the whole story.

At the worst point, in June 2024, food prices were rising 112% a year. Since August 2025 they've been falling, but they're still about 2.5x what they were in early 2023. And the fall isn't even. Staples like rice, beans and garri are about 35% off their peak. Meat, eggs and milk are only 4% off theirs.

![Grains vs protein](01-nigeria-food-prices/charts/grains_vs_protein.png)

[Read the full story](01-nigeria-food-prices/), or open the [Excel version](01-nigeria-food-prices/excel/naira_on_the_plate.xlsx) and pick any food to see its price since 2019.

### Late Parcels, Low Stars

We've all waited on a parcel that said "arriving today" and didn't. I went through 96,203 orders from Olist, a Brazilian marketplace, to see what that costs the store.

On-time orders average 4.28 stars. Late ones average 2.26. First-time buyers whose order came late were 25% less likely to order again. The good news is the problem is easy to find: just 98 of 2,945 sellers cause half of all late orders.

![Average review by delivery delay](04-olist-delivery-reviews/charts/reviews_by_delay.png)

[Read the full story](04-olist-delivery-reviews/).

## How each project is laid out

- `README.md` is the write-up
- `sql/` has the queries, numbered in the order they run
- `src/` has the scripts that download the data, load it into MySQL and run everything
- `outputs/` has the result tables. Every number in a write-up comes from here
- `charts/` has the charts

Raw data isn't saved in the repo. Each project tells you where to get it.

## Say hi

Email is the fastest way to reach me: okunolaolamide7@gmail.com
