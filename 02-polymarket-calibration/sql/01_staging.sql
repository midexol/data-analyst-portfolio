-- 01_staging.sql
-- One row per market per horizon (30, 7 or 1 day before it ended), from data/markets.csv (loaded as raw_markets).
DROP TABLE IF EXISTS forecasts;
CREATE TABLE forecasts AS
SELECT
    market_id,
    question,
    category,
    volume_usd,
    ended_at,
    horizon_days,
    price_yes,
    yes_won,
    -- 10 price buckets: 0 to 10%, 10 to 20%, ... 90 to 100%
    CAST(LEAST(FLOOR(price_yes * 10), 9) AS SIGNED) AS bucket,
    POWER(price_yes - yes_won, 2)                   AS sq_error
FROM raw_markets
WHERE price_yes BETWEEN 0 AND 1;

-- markets that were open long enough to have a price at all three horizons.
-- comparing horizons on these alone means the same questions are being scored each time.
DROP TABLE IF EXISTS all_three;
CREATE TABLE all_three AS
SELECT market_id FROM forecasts GROUP BY market_id HAVING count(DISTINCT horizon_days) = 3;
