-- 02_sender_concentration.sql
-- How concentrated is USDC payment volume among senders (last 12 full months)?
-- USDC issuer below is Circle's Stellar account; verify on stellar.expert before running.

WITH per_sender AS (
  SELECT `from` AS sender, SUM(SAFE_CAST(amount AS NUMERIC)) AS volume, COUNT(*) AS payments
  FROM `crypto-stellar.crypto_stellar_dbt.enriched_history_operations`
  WHERE closed_at >= (TIMESTAMP(DATE_SUB(DATE_TRUNC(CURRENT_DATE(), MONTH), INTERVAL 12 MONTH))) AND closed_at < (TIMESTAMP(DATE_TRUNC(CURRENT_DATE(), MONTH)))
    AND type = 1 AND asset_code = 'USDC' AND asset_issuer = 'GA5ZSEJYB37JRC5AVCIA5MOP4RHTM335X2KGX3IHOJAPP5RE34K4KZVN'
  GROUP BY sender
),
ranked AS (
  SELECT *,
         ROW_NUMBER() OVER (ORDER BY volume DESC) AS rnk,
         COUNT(*)     OVER ()                     AS n_senders,
         SUM(volume)  OVER ()                     AS total_volume
  FROM per_sender
)
SELECT
  ANY_VALUE(n_senders)                                                      AS senders,
  ROUND(ANY_VALUE(total_volume), 0)                                         AS total_volume_usdc,
  ROUND(100 * SUM(IF(rnk <= 10, volume, 0)) / ANY_VALUE(total_volume), 1)   AS pct_volume_top10,
  ROUND(100 * SUM(IF(rnk <= CEIL(n_senders * 0.01), volume, 0)) / ANY_VALUE(total_volume), 1) AS pct_volume_top1pct,
  ROUND(100 * SUM(IF(rnk <= CEIL(n_senders * 0.10), volume, 0)) / ANY_VALUE(total_volume), 1) AS pct_volume_top10pct
FROM ranked;
