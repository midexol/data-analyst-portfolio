-- 06_score_by_volume.sql
-- Do markets with more money in them predict better? Split at the median volume, one day before the end.
-- MySQL has no median(), so it's worked out from row numbers: the middle row, or the average of the middle two.
WITH day_before AS (
    SELECT * FROM forecasts WHERE horizon_days = 1
),
ordered AS (
    SELECT volume_usd,
           row_number() OVER (ORDER BY volume_usd) AS rn,
           count(*) OVER ()                        AS n
    FROM day_before
),
cutoff AS (
    SELECT avg(volume_usd) AS median_volume FROM ordered
    WHERE rn IN (FLOOR((n + 1) / 2), CEIL((n + 1) / 2))
),
m AS (
    SELECT d.*, d.volume_usd >= (SELECT median_volume FROM cutoff) AS big
    FROM day_before d
),
group_order AS (
    SELECT big, volume_usd,
           row_number() OVER (PARTITION BY big ORDER BY volume_usd) AS rn,
           count(*) OVER (PARTITION BY big)                        AS n
    FROM m
),
group_median AS (
    SELECT big, avg(volume_usd) AS median_volume FROM group_order
    WHERE rn IN (FLOOR((n + 1) / 2), CEIL((n + 1) / 2))
    GROUP BY big
)
SELECT
    CASE WHEN m.big THEN 'More money than the median' ELSE 'Less money than the median' END AS market_size,
    count(*)                                          AS markets,
    round(max(g.median_volume) / 1e6, 1)              AS median_volume_m_usd,
    round(avg(m.sq_error), 4)                         AS brier,
    round(avg(CASE WHEN m.price_yes BETWEEN 0.05 AND 0.95 THEN m.sq_error END), 4) AS brier_unsure_markets
FROM m
JOIN group_median g ON g.big = m.big
GROUP BY market_size
ORDER BY market_size;
