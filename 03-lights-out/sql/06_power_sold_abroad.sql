-- 06_power_sold_abroad.sql
-- Nigeria sells some of its grid power to neighbours. How much, compared with what it makes?
SELECT
    year,
    round(generation_twh, 2)                                 AS generation_twh,
    round(-net_imports_twh, 2)                               AS net_exports_twh,
    round(100 * -net_imports_twh / generation_twh, 1)        AS pct_of_generation_exported
FROM countries
WHERE country = 'Nigeria' AND net_imports_twh < 0
ORDER BY year;
