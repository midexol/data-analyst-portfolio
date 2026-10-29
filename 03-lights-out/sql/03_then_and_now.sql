-- 03_then_and_now.sql
-- Where each peer started (2000), where it is now (2024), and how fast it grew.
WITH ends AS (
    SELECT
        country,
        max(CASE WHEN year = 2000 THEN kwh_per_person END) AS kwh_2000,
        max(CASE WHEN year = 2024 THEN kwh_per_person END) AS kwh_2024,
        max(CASE WHEN year = 2000 THEN population END) AS pop_2000,
        max(CASE WHEN year = 2024 THEN population END) AS pop_2024
    FROM countries
    JOIN peers USING (country)
    GROUP BY country
)
SELECT
    country,
    round(kwh_2000, 0)                                         AS kwh_per_person_2000,
    round(kwh_2024, 0)                                         AS kwh_per_person_2024,
    round(kwh_2024 / kwh_2000, 2)                              AS times_bigger,
    -- average yearly growth over 24 years
    round(100 * (power(kwh_2024 / kwh_2000, 1e0 / 24) - 1), 1) AS growth_pct_per_year,
    round(pop_2000 / 1e6, 0)                                   AS population_2000_m,
    round(pop_2024 / 1e6, 0)                                   AS population_2024_m
FROM ends
ORDER BY kwh_per_person_2024;
