-- 03_score_by_horizon.sql
-- Brier score: the average squared gap between price and outcome. 0 is perfect, always saying 50% scores 0.25.
-- Only markets priced at all three horizons, so each row scores the same questions.
SELECT
    horizon_days,
    count(*)                                   AS markets,
    round(avg(sq_error), 4)                    AS brier,
    -- the same score, leaving out markets the crowd was already sure about (under 5% or over 95%)
    round(avg(CASE WHEN price_yes BETWEEN 0.05 AND 0.95 THEN sq_error END), 4) AS brier_unsure_markets,
    sum(price_yes BETWEEN 0.05 AND 0.95)                                       AS unsure_markets
FROM forecasts
WHERE market_id IN (SELECT market_id FROM all_three)
GROUP BY horizon_days
ORDER BY horizon_days DESC;
