-- 01_staging.sql
-- Clean tables from the raw World Bank file (loaded as raw_prices).
-- I use the "c_" (close) price for each food: the World Bank's monthly estimate,
-- which is filled in even where nobody collected a price that month.

-- Every month up to July 2026 (the last month with survey data; Aug 2026 is a nowcast)
DROP TABLE IF EXISTS prices_all;
CREATE TABLE prices_all AS
SELECT
    -- two real markets come with odd state labels: "National Average" is Abuja market,
    -- and "Kano State (1)" is Kano city market. Both have their own coordinates and
    -- collected prices, so I give them their proper state names (see 08_cleaning_log.sql)
    CASE adm1_name
        WHEN 'National Average' THEN 'FCT'
        WHEN 'Kano State (1)'   THEN 'Kano'
        ELSE adm1_name
    END                               AS state,
    mkt_name                          AS market,
    CAST(price_date AS DATE)          AS month,
    -- the only rows that aren't real markets: the national average and the 5 zone series
    adm1_name NOT IN ('Market Average', 'Geopolitical Zone') AS is_real_market,
    c_food_price_index                AS food_price_index,
    inflation_food_price_index        AS yoy_inflation_pct,
    -- estimated monthly prices (naira, in each food's own unit)
    c_beans, c_eggs, c_fish, c_gari_fao, c_groundnuts, c_maize_fao, c_maize_flour,
    c_meat_beef, c_meat_goat, c_milk, c_millet, c_onions, c_rice, c_rice_fao, c_sorghum_fao, c_yam,
    -- how many of the 16 foods had an actually collected price that month
      (beans IS NOT NULL) + (eggs IS NOT NULL) + (fish IS NOT NULL) +
      (gari_fao IS NOT NULL) + (groundnuts IS NOT NULL) + (maize_fao IS NOT NULL) + (maize_flour IS NOT NULL) +
      (meat_beef IS NOT NULL) + (meat_goat IS NOT NULL) + (milk IS NOT NULL) + (millet IS NOT NULL) +
      (onions IS NOT NULL) + (rice IS NOT NULL) + (rice_fao IS NOT NULL) + (sorghum_fao IS NOT NULL) + (yam IS NOT NULL)
                                      AS foods_observed,
    -- 1 kg rice + 1 kg beans + 1 kg garri (beans are priced per 2.5 kg)
    c_rice_fao + c_beans / 2.5 + c_gari_fao AS plate_ngn
FROM raw_prices
WHERE CAST(price_date AS DATE) <= DATE '2026-07-01';

-- The period I analyse
DROP TABLE IF EXISTS prices;
CREATE TABLE prices AS
SELECT * FROM prices_all WHERE month >= DATE '2019-01-01';

-- Long format for the national series: one row per month per food.
-- MySQL has no UNPIVOT, so each food is its own SELECT stacked with UNION ALL.
DROP TABLE IF EXISTS national_long;
CREATE TABLE national_long AS
SELECT month, 'beans' AS food, c_beans AS price FROM prices WHERE state = 'Market Average' AND c_beans IS NOT NULL
UNION ALL SELECT month, 'eggs' AS food, c_eggs AS price FROM prices WHERE state = 'Market Average' AND c_eggs IS NOT NULL
UNION ALL SELECT month, 'fish' AS food, c_fish AS price FROM prices WHERE state = 'Market Average' AND c_fish IS NOT NULL
UNION ALL SELECT month, 'gari_fao' AS food, c_gari_fao AS price FROM prices WHERE state = 'Market Average' AND c_gari_fao IS NOT NULL
UNION ALL SELECT month, 'groundnuts' AS food, c_groundnuts AS price FROM prices WHERE state = 'Market Average' AND c_groundnuts IS NOT NULL
UNION ALL SELECT month, 'maize_fao' AS food, c_maize_fao AS price FROM prices WHERE state = 'Market Average' AND c_maize_fao IS NOT NULL
UNION ALL SELECT month, 'maize_flour' AS food, c_maize_flour AS price FROM prices WHERE state = 'Market Average' AND c_maize_flour IS NOT NULL
UNION ALL SELECT month, 'meat_beef' AS food, c_meat_beef AS price FROM prices WHERE state = 'Market Average' AND c_meat_beef IS NOT NULL
UNION ALL SELECT month, 'meat_goat' AS food, c_meat_goat AS price FROM prices WHERE state = 'Market Average' AND c_meat_goat IS NOT NULL
UNION ALL SELECT month, 'milk' AS food, c_milk AS price FROM prices WHERE state = 'Market Average' AND c_milk IS NOT NULL
UNION ALL SELECT month, 'millet' AS food, c_millet AS price FROM prices WHERE state = 'Market Average' AND c_millet IS NOT NULL
UNION ALL SELECT month, 'onions' AS food, c_onions AS price FROM prices WHERE state = 'Market Average' AND c_onions IS NOT NULL
UNION ALL SELECT month, 'rice' AS food, c_rice AS price FROM prices WHERE state = 'Market Average' AND c_rice IS NOT NULL
UNION ALL SELECT month, 'rice_fao' AS food, c_rice_fao AS price FROM prices WHERE state = 'Market Average' AND c_rice_fao IS NOT NULL
UNION ALL SELECT month, 'sorghum_fao' AS food, c_sorghum_fao AS price FROM prices WHERE state = 'Market Average' AND c_sorghum_fao IS NOT NULL
UNION ALL SELECT month, 'yam' AS food, c_yam AS price FROM prices WHERE state = 'Market Average' AND c_yam IS NOT NULL;

-- Display names, units and the group each food belongs to
DROP TABLE IF EXISTS foods;
CREATE TABLE foods AS
          SELECT 'beans' AS food, 'Beans' AS label, '2.5 kg' AS unit, CAST('grains' AS CHAR(10)) AS food_group
UNION ALL SELECT 'eggs', 'Eggs (30)', '30 pcs', 'protein'
UNION ALL SELECT 'fish', 'Fish', '1 kg', NULL
UNION ALL SELECT 'gari_fao', 'Garri', '1 kg', 'grains'
UNION ALL SELECT 'groundnuts', 'Groundnuts', '2.2 kg', NULL
UNION ALL SELECT 'maize_fao', 'Maize', '1 kg', 'grains'
UNION ALL SELECT 'maize_flour', 'Maize flour', '2.1 kg', 'grains'
UNION ALL SELECT 'meat_beef', 'Beef', '1 kg', 'protein'
UNION ALL SELECT 'meat_goat', 'Goat meat', '1 kg', 'protein'
UNION ALL SELECT 'milk', 'Milk', '400 g', 'protein'
UNION ALL SELECT 'millet', 'Millet', '2.6 kg', 'grains'
UNION ALL SELECT 'onions', 'Onions', '0.5 kg', NULL
UNION ALL SELECT 'rice', 'Rice (local measure)', '2.8 kg', NULL
UNION ALL SELECT 'rice_fao', 'Rice', '1 kg', 'grains'
UNION ALL SELECT 'sorghum_fao', 'Sorghum', '1 kg', 'grains'
UNION ALL SELECT 'yam', 'Yam', '2.5 kg', NULL;
