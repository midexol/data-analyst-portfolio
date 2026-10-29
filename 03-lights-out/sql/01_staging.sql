-- 01_staging.sql
-- One clean row per country per year, 2000 to 2024, from Our World in Data's energy file (raw_energy).
--
-- Choices (all explained in 08_cleaning_log.sql):
--   * countries only: rows without an ISO code, or with an "OWID_" code, are regions like "Africa" or "World"
--   * 2000 onward: that's where Nigeria's electricity numbers start
--   * stop at 2024: only 90 countries have 2025 figures so far, so 2025 isn't a fair comparison year

DROP TABLE IF EXISTS countries;
CREATE TABLE countries AS
SELECT
    country,
    iso_code,
    year,
    population,
    electricity_generation   AS generation_twh,      -- electricity made in the country
    electricity_demand       AS demand_twh,          -- electricity used (generation + imports - exports)
    per_capita_electricity   AS kwh_per_person,      -- generation divided by population
    net_elec_imports         AS net_imports_twh,     -- negative means the country sells power abroad
    gas_share_elec           AS gas_pct,
    hydro_share_elec         AS hydro_pct,
    solar_share_elec         AS solar_pct,
    coal_share_elec          AS coal_pct,
    oil_share_elec           AS oil_pct
FROM raw_energy
WHERE iso_code IS NOT NULL
  AND iso_code NOT LIKE 'OWID%'
  AND year BETWEEN 2000 AND 2024;

-- The countries I compare Nigeria with, and why
DROP TABLE IF EXISTS peers;
CREATE TABLE peers AS
          SELECT 'Nigeria' AS country, 'Nigeria' AS why
UNION ALL SELECT 'Bangladesh', 'Started level with Nigeria in 2000, similar population'
UNION ALL SELECT 'Ethiopia',   'Started far behind Nigeria in 2000'
UNION ALL SELECT 'Ghana',      'West African neighbour'
UNION ALL SELECT 'Kenya',      'Similar income level in East Africa'
UNION ALL SELECT 'Vietnam',    'The fastest grower among large countries';
