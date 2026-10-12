-- 02_national_index.sql
-- The World Bank's food price index and year-on-year food inflation, national average.
SELECT
    month                          AS date,
    round(food_price_index, 3)     AS food_price_index,
    round(yoy_inflation_pct, 3)    AS yoy_inflation_pct
FROM prices
WHERE state = 'Market Average'
ORDER BY month;
