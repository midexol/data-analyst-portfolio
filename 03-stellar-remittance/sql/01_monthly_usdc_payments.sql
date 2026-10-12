-- 01_monthly_usdc_payments.sql
-- Monthly USDC payment activity on Stellar over the last 24 full months.
-- Run with --dry_run first: the closed_at filter is what keeps the scan (and bill) small.
-- USDC issuer below is Circle's Stellar account; verify on stellar.expert before running.

WITH payments AS (
  SELECT
    DATE_TRUNC(DATE(closed_at), MONTH) AS month,
    `from`                             AS sender,
    `to`                               AS receiver,
    SAFE_CAST(amount AS NUMERIC)       AS amount
  FROM `crypto-stellar.crypto_stellar_dbt.enriched_history_operations`
  WHERE closed_at >= (TIMESTAMP(DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 24 MONTH))) AND closed_at < (TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH)))
    AND type = 1                          -- payment
    AND asset_code = 'USDC'
    AND asset_issuer = 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN'
)
SELECT
  month,
  COUNT(*)                                       AS payments,
  ROUND(SUM(amount), 0)                          AS volume_usdc,
  COUNT(DISTINCT sender)                         AS unique_senders,
  COUNT(DISTINCT receiver)                       AS unique_receivers,
  ROUND(APPROX_QUANTILES(amount, 2)[OFFSET(1)], 2) AS median_payment_usdc,
  ROUND(100 * SAFE_DIVIDE(SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY month),
                          LAG(SUM(amount)) OVER (ORDER BY month)), 1) AS volume_mom_pct,
  ROUND(AVG(SUM(amount)) OVER (ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 0)
                                                 AS volume_rolling_3m
FROM payments
GROUP BY month
ORDER BY month;
