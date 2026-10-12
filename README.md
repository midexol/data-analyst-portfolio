# data-analyst-portfolio

Hey, I'm Mide. I'm a CS student at FUTA and this is where I keep my data analysis projects. Every project here uses public data, so you can rerun everything yourself and check my numbers.

## Projects

| Project | What I wanted to know | Tools | Where it's at |
| --- | --- | --- | --- |
| [Late Parcels, Low Stars](04-olist-delivery-reviews/) | How much do late deliveries hurt reviews and repeat orders? | SQL (DuckDB), Python, SciPy | Done |
| [Do Prediction Markets Know?](02-polymarket-calibration/) | When Polymarket says 70%, does it actually happen 70% of the time? | Python, REST APIs | Code ready, haven't run it yet |
| [Naira on the Plate](01-nigeria-food-prices/) | Which staple foods got the most expensive in 2024-25, and where? | Python, Power BI | Code ready, waiting on data download |
| [Remittance Rails](03-stellar-remittance/) | How fast is USDC payment activity growing on Stellar? | BigQuery SQL | Queries ready, need to run on my GCP |

## The one that's finished

I took about 96k orders from Olist (a Brazilian marketplace) and looked at what happens when deliveries show up late. Short version: late orders average 2.26 stars vs 4.28 for on-time ones, people whose first order was late were about 25% less likely to order again, and just 98 out of 2,945 sellers are behind half the late orders.

![Average review by delivery delay](04-olist-delivery-reviews/charts/reviews_by_delay.png)

Full write-up is [here](04-olist-delivery-reviews/).

## How the folders work

Each project folder has the same layout:

- `README.md` - the write-up
- `sql/` - queries, numbered in the order they run
- `src/` - scripts for downloading data and running the analysis
- `outputs/` - the result tables (every number in a README comes from these)
- `charts/`

Raw data isn't committed, each project has a script or instructions to get it.

Find me on GitHub: [@midexol](https://github.com/midexol)
