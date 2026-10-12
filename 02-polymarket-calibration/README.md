# Do Prediction Markets Know?

When Polymarket prices something at 70%, does it actually happen about 70% of the time? And do the prices get more accurate as the resolution date gets closer?

I've built prediction market trading bots before, so I wanted to test how good the "wisdom of the crowd" really is.

**Status:** the pipeline is written and tested, but I haven't done the full data pull yet. Findings coming soon.

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
4. Calibration curve: bucket the prices into 10 bins and compare the average price in each bin to how often YES actually happened (with 95% confidence intervals)
5. Brier score by horizon, category and volume. Lower is better, and always guessing 50% scores 0.25

## Running it

```bash
pip install -r requirements.txt
python src/fetch.py --per-tag 150   # takes 20-40 min the first time, responses get cached
python src/analyze.py
```

Results go to `outputs/` and the calibration chart to `charts/calibration.png`.

## Things to keep in mind

- A market can have more than one tag
- Leaving out voided markets slightly favours markets with clean outcomes
- Sampling by tag isn't a random sample of every market on the platform
