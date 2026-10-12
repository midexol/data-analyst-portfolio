# Remittance Rails

How is USDC payment activity on Stellar growing, how much of it comes from a few big senders, and do new senders keep using it?

I've been building cross-border payment stuff on Stellar, so I wanted to see what's actually happening on-chain.

**Status:** queries are written. I need to run them on my own Google Cloud project since BigQuery bills whoever runs the query.

Tools: BigQuery SQL (CTEs, window functions, cohort tables), Looker Studio

## Data

[Hubble](https://developers.stellar.org/docs/data/analytics/hubble) is the Stellar Development Foundation's public BigQuery copy of the whole network history. The queries read `crypto-stellar.crypto_stellar_dbt.enriched_history_operations` and filter to:

- `type = 1` (plain payments, I left out path payments so the asset is never ambiguous)
- USDC issued by Circle (double-check the issuer address on stellar.expert first)
- a date range on `closed_at` in every query, which keeps the scan and the bill small

## Queries

| File | What it answers |
| --- | --- |
| [`01_monthly_usdc_payments.sql`](sql/01_monthly_usdc_payments.sql) | Monthly payments, volume, unique senders and receivers, median payment size, month-over-month growth, 3-month rolling average |
| [`02_sender_concentration.sql`](sql/02_sender_concentration.sql) | How much of the last 12 months' volume came from the top 10 senders, top 1% and top 10% |
| [`03_sender_cohorts.sql`](sql/03_sender_cohorts.sql) | Of the people who first sent USDC in a given month, how many were still sending 1-6 months later |

## Running it

```bash
gcloud auth login
gcloud auth application-default login
export GCP_PROJECT=your-project-id   # needs billing on, set a budget alert first
bash src/run_queries.sh
```

The script dry-runs each query first and won't run anything that would scan more than about 200 GB (you can change that with `MAX_BYTES`). Results get saved as CSVs in `outputs/`.

For the dashboard, Looker Studio can connect straight to Hubble ([guide](https://developers.stellar.org/docs/data/analytics/hubble/analyst-guide/connecting)).
