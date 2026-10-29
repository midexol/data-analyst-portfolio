-- 02_calibration.sql
-- When the price said X%, how often did YES actually happen? With a 95% range (Wilson interval).
WITH b AS (
    SELECT horizon_days, bucket,
           count(*)             AS markets,
           avg(price_yes)       AS avg_price,
           avg(yes_won * 1e0)   AS yes_rate      -- * 1e0 keeps full precision (avg of whole numbers is cut to 4 places)
    FROM forecasts
    GROUP BY horizon_days, bucket
)
SELECT
    horizon_days,
    CONCAT(bucket * 10, ' to ', bucket * 10 + 10, '%') AS price_range,
    markets,
    round(100 * avg_price, 1) AS avg_price_pct,
    round(100 * yes_rate, 1)  AS happened_pct,
    round(100 * (yes_rate + POWER(1.96, 2) / (2 * markets)
        - 1.96 * sqrt(yes_rate * (1 - yes_rate) / markets + POWER(1.96, 2) / (4 * POWER(markets, 2))))
        / (1 + POWER(1.96, 2) / markets), 1) AS low_pct,
    round(100 * (yes_rate + POWER(1.96, 2) / (2 * markets)
        + 1.96 * sqrt(yes_rate * (1 - yes_rate) / markets + POWER(1.96, 2) / (4 * POWER(markets, 2))))
        / (1 + POWER(1.96, 2) / markets), 1) AS high_pct
FROM b
ORDER BY horizon_days DESC, bucket;
