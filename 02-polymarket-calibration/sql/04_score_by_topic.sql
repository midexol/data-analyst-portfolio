-- 04_score_by_topic.sql
-- Which topics does the crowd call best? Brier score one day before the end.
SELECT
    category,
    count(*)                                   AS markets,
    round(avg(sq_error), 4)                    AS brier,
    round(avg(CASE WHEN price_yes BETWEEN 0.05 AND 0.95 THEN sq_error END), 4) AS brier_unsure_markets,
    round(100 * avg(yes_won * 1e0), 1)         AS pct_yes_won
FROM forecasts
WHERE horizon_days = 1
GROUP BY category
ORDER BY brier;
