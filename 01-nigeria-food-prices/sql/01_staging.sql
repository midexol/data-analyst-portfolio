-- 01_staging.sql
-- Clean tables from the raw World Bank file (loaded as raw_prices).
-- I use the "c_" (close) price for each food: the World Bank's monthly estimate,
-- which is filled in even where nobody collected a price that month.

-- Every month up to July 2026 (the last month with survey data; Aug 2026 is a nowcast)
CREATE OR REPLACE TABLE prices_all AS
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
      (beans IS NOT NULL)::INT + (eggs IS NOT NULL)::INT + (fish IS NOT NULL)::INT
    + (gari_fao IS NOT NULL)::INT + (groundnuts IS NOT NULL)::INT + (maize_fao IS NOT NULL)::INT
    + (maize_flour IS NOT NULL)::INT + (meat_beef IS NOT NULL)::INT + (meat_goat IS NOT NULL)::INT
    + (milk IS NOT NULL)::INT + (millet IS NOT NULL)::INT + (onions IS NOT NULL)::INT
    + (rice IS NOT NULL)::INT + (rice_fao IS NOT NULL)::INT + (sorghum_fao IS NOT NULL)::INT
    + (yam IS NOT NULL)::INT          AS foods_observed,
    -- 1 kg rice + 1 kg beans + 1 kg garri (beans are priced per 2.5 kg)
    c_rice_fao + c_beans / 2.5 + c_gari_fao AS plate_ngn
FROM raw_prices
WHERE CAST(price_date AS DATE) <= DATE '2026-07-01';

-- The period I analyse
CREATE OR REPLACE TABLE prices AS
SELECT * FROM prices_all WHERE month >= DATE '2019-01-01';

-- Long format for the national series: one row per month per food
CREATE OR REPLACE TABLE national_long AS
UNPIVOT (
    SELECT month, c_beans AS beans, c_eggs AS eggs, c_fish AS fish, c_gari_fao AS gari_fao,
           c_groundnuts AS groundnuts, c_maize_fao AS maize_fao, c_maize_flour AS maize_flour,
           c_meat_beef AS meat_beef, c_meat_goat AS meat_goat, c_milk AS milk, c_millet AS millet,
           c_onions AS onions, c_rice AS rice, c_rice_fao AS rice_fao, c_sorghum_fao AS sorghum_fao, c_yam AS yam
    FROM prices
    WHERE state = 'Market Average'
)
ON beans, eggs, fish, gari_fao, groundnuts, maize_fao, maize_flour, meat_beef, meat_goat,
   milk, millet, onions, rice, rice_fao, sorghum_fao, yam
INTO NAME food VALUE price;

-- Display names, units and the group each food belongs to
CREATE OR REPLACE TABLE foods AS
SELECT * FROM (VALUES
    ('beans',       'Beans',                '2.5 kg', 'grains'),
    ('eggs',        'Eggs (30)',            '30 pcs', 'protein'),
    ('fish',        'Fish',                 '1 kg',   NULL),
    ('gari_fao',    'Garri',                '1 kg',   'grains'),
    ('groundnuts',  'Groundnuts',           '2.2 kg', NULL),
    ('maize_fao',   'Maize',                '1 kg',   'grains'),
    ('maize_flour', 'Maize flour',          '2.1 kg', 'grains'),
    ('meat_beef',   'Beef',                 '1 kg',   'protein'),
    ('meat_goat',   'Goat meat',            '1 kg',   'protein'),
    ('milk',        'Milk',                 '400 g',  'protein'),
    ('millet',      'Millet',               '2.6 kg', 'grains'),
    ('onions',      'Onions',               '0.5 kg', NULL),
    ('rice',        'Rice (local measure)', '2.8 kg', NULL),
    ('rice_fao',    'Rice',                 '1 kg',   'grains'),
    ('sorghum_fao', 'Sorghum',              '1 kg',   'grains'),
    ('yam',         'Yam',                  '2.5 kg', NULL)
) AS t(food, label, unit, food_group);
