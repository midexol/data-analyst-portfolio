-- 05_underdogs.sql
-- Underdogs: bets priced 10 to 40%. Did they happen as often as the price said? All horizons together.
SELECT
    CASE WHEN price_yes < 0.10 THEN '1. under 10%'
         WHEN price_yes < 0.40 THEN '2. 10 to 40%'
         WHEN price_yes < 0.60 THEN '3. 40 to 60%'
         WHEN price_yes < 0.90 THEN '4. 60 to 90%'
         ELSE                       '5. 90% and up' END AS price_group,
    count(*)                                AS forecasts,
    round(100 * avg(price_yes), 1)          AS avg_price_pct,
    round(100 * avg(yes_won * 1e0), 1)      AS happened_pct,
    round(100 * (avg(yes_won * 1e0) - avg(price_yes)), 1) AS gap_pts
FROM forecasts
GROUP BY price_group
ORDER BY price_group;
