-- 02_per_person.sql
-- Electricity per person (kWh) for Nigeria and its peers, every year 2000 to 2024.
SELECT
    c.year,
    c.country,
    round(CAST(c.kwh_per_person AS DECIMAL(20, 6)), 1) AS kwh_per_person  -- exact decimal, so halves round up
FROM countries c
JOIN peers p USING (country)
ORDER BY c.country, c.year;
