-- 04_more_power_more_people.sql
-- Nigeria made more electricity every decade, but the population grew too.
-- Both indexed to 2000 = 100 so they can share one chart.
WITH ng AS (
    SELECT year, generation_twh, population, kwh_per_person
    FROM countries WHERE country = 'Nigeria'
),
base AS (SELECT * FROM ng WHERE year = 2000)
SELECT
    ng.year,
    round(ng.generation_twh, 2)                                AS generation_twh,
    round(ng.population / 1e6, 1)                              AS population_m,
    round(100 * ng.generation_twh / base.generation_twh, 1)    AS generation_index,
    round(100 * ng.population / base.population, 1)            AS population_index,
    round(100 * ng.kwh_per_person / base.kwh_per_person, 1)    AS per_person_index
FROM ng, base
ORDER BY ng.year;
