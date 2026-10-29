-- 07_upsets.sql
-- The crowd's biggest misses: things priced at 85% or more one day before that didn't happen, and the reverse.
SELECT
    category,
    question,
    round(CAST(100 * price_yes AS DECIMAL(20, 6)), 1) AS price_pct_day_before,  -- exact decimal, so halves round up
    CASE WHEN yes_won = 1 THEN 'Yes' ELSE 'No' END AS what_happened,
    round(volume_usd / 1e6, 1) AS volume_m_usd
FROM forecasts
WHERE horizon_days = 1
  AND ((price_yes >= 0.85 AND yes_won = 0) OR (price_yes <= 0.15 AND yes_won = 1))
ORDER BY abs(price_yes - yes_won) DESC, market_id
LIMIT 15;
