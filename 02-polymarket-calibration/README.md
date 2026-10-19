# Do Prediction Markets Know?

On Polymarket, people bet real money on things like elections, football matches and crypto prices. The price of a bet works like a forecast. If "yes" costs 70 cents, the crowd is saying there's a 70% chance it happens.

So here's the question: when the crowd says 70%, does it actually happen about 70% of the time? And does the crowd get more accurate as the big day gets closer?

I've built trading bots for these markets, so I've always wanted to know how much to trust the price.

**Status:** the code is written and tested, but I haven't run the full data pull yet. Findings coming soon.

Tools: Python (requests, pandas, NumPy, matplotlib)

## Data

Both APIs are public, no key needed.

- [Gamma API](https://docs.polymarket.com/market-data/discover-markets.md) - lists resolved markets with their YES/NO token IDs and volume
- [Data API v2 prices-history](https://docs.polymarket.com/cn/api-reference/endpoints/data-v2/get-prices-history.md) - price history for each token

One nice detail: for a resolved market, the last point in the price history is the on-chain payout (1 or 0). So one call gives me both the outcome and the exact time it resolved. Then `as_of=` lets me grab the price at any point before that.

## Plan

1. Pull ~150 resolved yes/no markets each from politics, sports, crypto and economy
2. Skip anything that was voided or didn't resolve cleanly
3. Grab the YES price 30, 7 and 1 day before resolution
4. Group the prices into 10 buckets (0 to 10%, 10 to 20%, and so on) and check how often "yes" actually happened in each one. If the market is honest, the 70% bucket should come true about 70% of the time
5. Score how close the prices were overall (the Brier score), split by how far out, by topic, and by how much money was traded. Lower is better. Guessing 50% every time scores 0.25, so anything below that beats a coin flip

## Running it

```bash
pip install -r requirements.txt
python src/fetch.py --per-tag 150   # takes 20-40 min the first time, responses get cached
python src/analyze.py
```

Results go to `outputs/` and the calibration chart to `charts/calibration.png`.

## What this won't tell you

- A market can have more than one tag
- Leaving out voided markets slightly favours markets with clean outcomes
- Sampling by tag isn't a random sample of every market on the platform
