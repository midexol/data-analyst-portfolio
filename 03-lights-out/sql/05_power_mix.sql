-- 05_power_mix.sql
-- Where Nigeria's grid electricity comes from, by year (shares of generation, %).
SELECT
    year,
    round(gas_pct, 1)                                               AS gas_pct,
    round(hydro_pct, 1)                                             AS hydro_pct,
    round(solar_pct, 2)                                             AS solar_pct,
    round(100 - coalesce(gas_pct, 0) - coalesce(hydro_pct, 0) - coalesce(solar_pct, 0), 2) AS other_pct
FROM countries
WHERE country = 'Nigeria'
ORDER BY year;
