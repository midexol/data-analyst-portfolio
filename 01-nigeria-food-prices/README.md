# Naira on the Plate

Which staple foods got the most expensive in Nigeria in 2024-25, in which states, and how much gets added between the farm and the market?

Food prices are something everyone around me talks about, so I wanted to look at the actual numbers.

**Status:** the code is ready. I still need to download the World Bank data (it needs a free account).

Tools: Python (pandas, matplotlib), Power BI for the dashboard

## Data

- [World Bank / NBS crowdsourced food prices, Nigeria 2024-2025](https://microdata.worldbank.org/catalog/8197/study-description): 10 staples (local and imported rice, white and yellow maize, white and brown beans, garri, yam, sorghum, soybean), with retail, wholesale and farmgate prices in naira per kg. You need to register, then download the `level2_price_*` files into `data/raw/`.
- [FEWS NET weekly staple prices for Nigeria (HDX)](https://data.humdata.org/m/dataset/fewsnet_staple_food_price_data_for_nigeria_weekly_6837): weekly prices from March 2021 to August 2024, useful for a longer baseline. Download the CSV into `data/raw/`.

## What the scripts do

[`prepare.py`](src/prepare.py) reads everything in `data/raw/` into one table (date, state, market, commodity, price type, naira per kg). The two sources name their columns differently, so it checks a list of possible names and tells you if it can't find one. It also converts bag prices (5-100 kg) to per kg and drops the top and bottom 1% of prices as likely typos.

[`analyze.py`](src/analyze.py) then works out:

- monthly median prices by state, commodity and price type (this is the table Power BI reads)
- a national retail price index with January 2024 = 100, plus year-on-year change
- the markup from farm gate to retail, by state
- a "plate cost": rice + beans + garri per kg added together, so states can be compared with one number

## Running it

```bash
pip install -r requirements.txt
python src/prepare.py
python src/analyze.py
```

## Things to keep in mind

- The prices are crowdsourced, so some states and weeks have a lot more submissions than others. I used medians to keep outliers from skewing things.
- Unit conversion depends on how each file writes its units, so check the `prepare.py` output for anything it didn't recognise.
