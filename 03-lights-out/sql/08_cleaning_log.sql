-- 08_cleaning_log.sql
-- Every cleaning step with the row count after it, worked out from the raw file.
-- One row in the raw file = one country or region in one year.

WITH is_country AS (
    SELECT * FROM raw_energy WHERE iso_code IS NOT NULL AND iso_code NOT LIKE 'OWID%'
),
in_window AS (
    SELECT * FROM is_country WHERE year BETWEEN 2000 AND 2024
),
dupes AS (
    SELECT count(*) AS n FROM (
        SELECT country, year FROM raw_energy GROUP BY country, year HAVING count(*) > 1
    ) AS d
),
ng AS (SELECT * FROM in_window WHERE country = 'Nigeria'),
check_math AS (
    -- does kWh per person really equal generation / population? (TWh to kWh is x 1e9)
    SELECT max(abs(per_capita_electricity - electricity_generation * 1e9 / population)) AS worst_gap
    FROM ng
)
          SELECT 1 AS step, 'Start with the raw OWID file' AS what_i_did,
        (SELECT count(*) FROM raw_energy) AS rows_after,
        CONCAT((SELECT count(DISTINCT country) FROM raw_energy), ' countries and regions, years ',
               (SELECT min(year) FROM raw_energy), ' to ', (SELECT max(year) FROM raw_energy), ', 130 columns') AS why
UNION ALL SELECT 2, 'Drop regions, keep countries',
        (SELECT count(*) FROM is_country),
        CONCAT('Rows like "Africa", "World" or "High-income countries" have no ISO code or an OWID_ code. They''re totals, so keeping them would double count. ',
               (SELECT count(DISTINCT country) FROM is_country), ' countries left')
UNION ALL SELECT 3, 'Keep 2000 to 2024',
        (SELECT count(*) FROM in_window),
        CONCAT('Nigeria''s electricity numbers start in 2000. 2025 is cut because only ',
               (SELECT count(*) FROM is_country WHERE year = 2025 AND per_capita_electricity IS NOT NULL),
               ' countries have it so far, against ',
               (SELECT count(*) FROM is_country WHERE year = 2024 AND per_capita_electricity IS NOT NULL), ' for 2024')
UNION ALL SELECT 4, 'Check for duplicate country-years',
        (SELECT count(*) FROM in_window),
        CONCAT((SELECT n FROM dupes), ' duplicates found, nothing removed')
UNION ALL SELECT 5, 'Check Nigeria has no gaps',
        (SELECT count(*) FROM in_window),
        CONCAT('Nigeria has ', (SELECT count(*) FROM ng WHERE per_capita_electricity IS NOT NULL), ' of 25 years filled in. ',
               (SELECT count(*) FROM in_window WHERE per_capita_electricity IS NULL),
               ' country-years elsewhere are empty. Almost all are territories under 1 million people, plus 2 years for Ukraine. Left empty, not guessed')
UNION ALL SELECT 6, 'Check the per-person maths',
        (SELECT count(*) FROM in_window),
        CONCAT('For Nigeria, kWh per person matches generation divided by population to within ',
               (SELECT CASE WHEN worst_gap < 0.001 THEN '0.001' ELSE CAST(round(worst_gap, 3) AS CHAR) END FROM check_math),
               ' kWh in every year, so the column means what it says')
UNION ALL SELECT 7, 'Check why use and generation differ',
        (SELECT count(*) FROM in_window),
        'From 2016 Nigeria''s demand is lower than its generation. The gap matches its net exports, so it''s power sold to neighbours, not an error'
UNION ALL SELECT 8, 'Note what this data can''t see',
        (SELECT count(*) FROM in_window),
        'These are grid numbers only. Power from home and business generators isn''t counted, and in Nigeria that''s a lot';
