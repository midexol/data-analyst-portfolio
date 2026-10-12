# Late Parcels, Low Stars

Analysing how late deliveries affect reviews and repeat purchases on Olist, a Brazilian e-commerce marketplace.

**TL;DR:** late orders average **2.26 stars** compared to **4.28** for on-time ones. Customers whose first order came late were about **25% less likely** to buy again. And it's not spread evenly: **98 of 2,945 sellers** account for half of all late orders.

Tools: SQL (DuckDB), Python (pandas, SciPy, matplotlib)
Data: [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), 96,203 delivered orders from Jan 2017 to Aug 2018

## Why I looked at this

Every marketplace promises a delivery date at checkout. I wanted to put a number on what it costs when that promise gets broken, and figure out whether the problem is everywhere or concentrated in a few places an ops team could actually fix.

So three questions:

1. How much does a late delivery hurt the review score?
2. Does it hurt repeat business too?
3. Where do the late deliveries come from?

## Data and setup

The dataset has 9 tables. I used four of them: orders (dates and status), reviews (1-5 stars), customers (state, plus a unique ID that follows a person across orders) and order items (which seller shipped what).

A few decisions worth knowing about:

- I only kept **delivered** orders placed between Jan 2017 and Aug 2018. The months before and after that only have a handful of orders.
- An order counts as **late** if it arrived on a later calendar day than the estimated date shown at checkout.
- Some orders have more than one review, so I kept the most recent one.

## How I did it

1. Built a clean one-row-per-order table in SQL ([`01_staging.sql`](sql/01_staging.sql))
2. Grouped orders by how late they were and compared review scores ([`02`](sql/02_delivery_vs_reviews.sql))
3. Looked at late rates by month, by state and by seller ([`03`](sql/03_late_rate_by_month.sql), [`04`](sql/04_late_rate_by_state.sql), [`05`](sql/05_seller_late_rates.sql))
4. Compared repeat purchase rates for customers whose first order was late vs on time ([`06`](sql/06_repeat_purchase.sql))
5. Did an RFM segmentation to see which customers bring in the money ([`07`](sql/07_rfm_segments.sql))
6. Ran a Mann-Whitney U test on the review scores and a chi-square test on the repeat rates ([`run_analysis.py`](src/run_analysis.py))

## What I found

### Reviews drop off fast

![Average review by delivery delay](charts/reviews_by_delay.png)

| Delivered | Orders | Avg review | 1-2 star reviews | 5 star reviews |
| --- | ---: | ---: | ---: | ---: |
| On time or early | 89,672 | 4.28 | 9.5% | 62.0% |
| 1-3 days late | 1,869 | 3.28 | 32.4% | 33.1% |
| 4-7 days late | 1,802 | 2.09 | 68.1% | 13.7% |
| 8-14 days late | 1,478 | 1.67 | 80.4% | 6.8% |
| 15+ days late | 1,382 | 1.72 | 78.5% | 7.1% |

Even 1-3 days late more than triples the share of 1-2 star reviews. Once you're more than a week late, about 4 in 5 reviews are 1 or 2 stars. The difference between on-time and late is statistically significant (Mann-Whitney U, p < 0.001) and the effect is big (rank-biserial correlation of 0.64).

### Late first orders mean fewer repeat customers

![Repeat purchase by first experience](charts/repeat_by_first_experience.png)

I only included customers whose first order was before March 2018, so everyone had at least 6 months to come back. 4.04% of customers with an on-time first order bought again, vs 3.02% when the first order was late. That's roughly a 25% relative drop (chi-square = 9.1, p = 0.003).

Repeat buying is rare on Olist in general, so the absolute numbers are small. But it stacks on top of the bad review.

### It's concentrated in time, place and sellers

![Late rate by month](charts/late_rate_by_month.png)

- **When:** normally around 3-4% of orders are late. That jumped to 12.4% after Black Friday (Nov 2017), then 14.1% in Feb 2018 and 19.0% in March 2018, before going back to normal in April.
- **Where:** Rio de Janeiro has 12.8% of all orders but 22.9% of the late ones. Its late rate (12.1%) is 2.7x São Paulo's (4.5%). The Northeast is worst, with Maranhão at 17.5%.
- **Who:** 98 of 2,945 sellers (3.3%) are responsible for half of all late orders. The full ranking is in [`outputs/05_seller_late_rates.csv`](outputs/05_seller_late_rates.csv).

![Late rate by state](charts/late_rate_by_state.png)

### A small group brings in most of the revenue

![RFM segments](charts/rfm_customers_vs_revenue.png)

The top quarter of customers by spend are 23% of customers but 55% of revenue. Only 2.9% of customers have ordered more than once, so there isn't really a loyal base to protect yet. The bigger opportunity is getting a second order out of first-time big spenders.

## What I'd recommend

1. **Get the first order right.** Add a 2-3 day buffer to the estimated delivery date for first-time customers. A slightly longer promise costs less than a 1-star review and a customer who never comes back.
2. **Watch the worst sellers.** Around 100 sellers cause half the late orders. Monthly on-time scorecards for them would go a lot further than trying to fix the whole network.
3. **Plan for the peaks.** Pad estimates for Rio and the Northeast, and around Black Friday and Feb-Mar, instead of promising the same timeline everywhere.

Next thing I'd want to test: whether padding the estimate actually improves reviews (an A/B test on the delivery promise), and how much revenue the lost repeat orders are worth.

## Limitations

- The data only has orders that were eventually delivered. Orders still in transit when the data was pulled are missing, so the last few months probably look better than they really were.
- The repeat purchase result is a correlation. Customers who got late orders might be different in other ways, like where they live.
- If one order had items from multiple sellers, it counts toward each of them in the seller analysis.

## Running it yourself

```bash
pip install -r requirements.txt
bash src/get_data.sh
python src/run_analysis.py
```

All the numbers above come from the files in [`outputs/`](outputs/). [`summary.json`](outputs/summary.json) has the headline stats and test results.
