-- 07_world_rank.sql
-- In 2024, among countries with 30 million+ people, who has less grid electricity per person than Nigeria?
WITH big AS (
    SELECT country, population, kwh_per_person
    FROM countries
    WHERE year = 2024 AND population >= 30e6 AND kwh_per_person IS NOT NULL
)
SELECT
    rank() OVER (ORDER BY kwh_per_person)       AS rank_from_bottom,
    country,
    round(population / 1e6, 0)                  AS population_m,
    round(kwh_per_person, 0)                    AS kwh_per_person,
    (SELECT count(*) FROM big)                  AS countries_ranked
FROM big
ORDER BY kwh_per_person;
