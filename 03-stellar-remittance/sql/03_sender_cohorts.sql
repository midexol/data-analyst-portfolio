-- 03_sender_cohorts.sql
-- Sender retention: of accounts that first sent USDC in month M, what share sent again in M+1..M+6?
-- USDC issuer below is Circle's Stellar account; verify on stellar.expert before running.

WITH active AS (
  SELECT DISTINCT `from` AS sender, DATE_TRUNC(DATE(closed_at), MONTH) AS month
  FROM `crypto-stellar.crypto_stellar_dbt.enriched_history_operations`
  WHERE closed_at >= (TIMESTAMP(DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 18 MONTH))) AND closed_at < (TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH)))
    AND type = 1 AND asset_code = 'USDC' AND asset_issuer = 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN'
),
firsts AS (SELECT sender, MIN(month) AS cohort FROM active GROUP BY sender),
grid AS (
  SELECT f.cohort, DATE_DIFF(a.month, f.cohort, MONTH) AS months_since, COUNT(DISTINCT a.sender) AS senders
  FROM firsts f JOIN active a USING (sender)
  GROUP BY 1, 2
)
SELECT
  cohort,
  months_since,
  senders,
  ROUND(100 * senders / FIRST_VALUE(senders) OVER (PARTITION BY cohort ORDER BY months_since), 1) AS pct_retained
FROM grid
WHERE months_since <= 6
  AND cohort >= DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 17 MONTH)  -- first month mixes old and new senders
ORDER BY cohort, months_since;
