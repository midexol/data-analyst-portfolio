-- 07_observed_share.sql
-- What share of prices were actually collected (not estimated), by year, real markets only.
SELECT
    year(month)                                  AS year,
    round(avg(100.0 * foods_observed / 16), 1)   AS pct_prices_observed
FROM prices_all
WHERE is_real_market
GROUP BY year(month)
ORDER BY year;
