-- 08_cleaning_log.sql
-- Every cleaning step, with the row counts before and after, worked out from the raw file.
-- One row in the raw file = one price series (a market, a zone, or the national average) in one month.

WITH raw AS (
    SELECT *, CAST(price_date AS DATE) AS price_month FROM raw_prices
),
in_window AS (
    SELECT * FROM raw WHERE price_month BETWEEN DATE '2019-01-01' AND DATE '2026-07-01'
),
dupes AS (
    SELECT count(*) AS n FROM (
        SELECT adm1_name, mkt_name, price_month FROM raw GROUP BY adm1_name, mkt_name, price_month HAVING count(*) > 1
    ) AS d
),
missing AS (
    -- estimated prices that are empty, across all 16 foods, inside the window I use
    SELECT
            sum(c_beans IS NULL) + sum(c_eggs IS NULL) + sum(c_fish IS NULL) + sum(c_gari_fao IS NULL)
          + sum(c_groundnuts IS NULL) + sum(c_maize_fao IS NULL) + sum(c_maize_flour IS NULL) + sum(c_meat_beef IS NULL)
          + sum(c_meat_goat IS NULL) + sum(c_milk IS NULL) + sum(c_millet IS NULL) + sum(c_onions IS NULL)
          + sum(c_rice IS NULL) + sum(c_rice_fao IS NULL) + sum(c_sorghum_fao IS NULL) + sum(c_yam IS NULL) AS n
    FROM in_window
    WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone')
),
collected AS (
    -- share of market prices that were actually collected, not estimated by the model
    SELECT round(100 * avg((
            (beans IS NOT NULL) + (eggs IS NOT NULL) + (fish IS NOT NULL) + (gari_fao IS NOT NULL)
          + (groundnuts IS NOT NULL) + (maize_fao IS NOT NULL) + (maize_flour IS NOT NULL) + (meat_beef IS NOT NULL)
          + (meat_goat IS NOT NULL) + (milk IS NOT NULL) + (millet IS NOT NULL) + (onions IS NOT NULL)
          + (rice IS NOT NULL) + (rice_fao IS NOT NULL) + (sorghum_fao IS NOT NULL) + (yam IS NOT NULL)) * 1e0) / 16, 1) AS pct
    FROM in_window
    WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone')
)
          SELECT 1 AS step, 'Start with the raw World Bank file' AS what_i_did,
        (SELECT count(*) FROM raw) AS rows_after,
        CONCAT((SELECT count(DISTINCT CONCAT(adm1_name, '|', mkt_name)) FROM raw), ' price series, ',
               (SELECT count(DISTINCT price_month) FROM raw), ' months (Jan 2007 to Aug 2026), 137 columns') AS why
UNION ALL SELECT 2, 'Drop August 2026',
        (SELECT count(*) FROM raw WHERE price_month <= DATE '2026-07-01'),
        'The file says its last real survey was July 2026, so August is a forecast, not data'
UNION ALL SELECT 3, 'Keep January 2019 onward',
        (SELECT count(*) FROM in_window),
        'Earlier years are much thinner (under 10% of prices collected before 2017). 2019 also gives four full years before the 2023 jump to compare against'
UNION ALL SELECT 4, 'Check for duplicate market-months',
        (SELECT count(*) FROM in_window),
        CONCAT((SELECT n FROM dupes), ' duplicates found, nothing removed')
UNION ALL SELECT 5, 'Sort the rows into three kinds',
        (SELECT count(*) FROM in_window),
        CONCAT((SELECT count(DISTINCT mkt_name) FROM in_window WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone')),
               ' real markets, 5 zone series, 1 national average. Nothing removed, they''re just used for different things')
UNION ALL SELECT 6, 'Fix two mislabelled markets',
        (SELECT count(*) FROM in_window),
        '"National Average" is really Abuja market and "Kano State (1)" is really Kano city market. Both have their own coordinates and collected prices, so I renamed their states to FCT and Kano and counted them as markets'
UNION ALL SELECT 7, 'Check for missing prices',
        (SELECT count(*) FROM in_window),
        CONCAT((SELECT n FROM missing), ' empty estimated prices in the window, so no filling needed')
UNION ALL SELECT 8, 'Note how much is estimated',
        (SELECT count(*) FROM in_window),
        CONCAT('Only ', (SELECT pct FROM collected), '% of market prices since 2019 were actually collected. The rest are World Bank model estimates. Kept, but flagged in the write-up')
UNION ALL SELECT 9, 'Put prices on the same footing',
        (SELECT count(*) FROM in_window),
        'Each food has its own unit (beans per 2.5 kg, eggs per 30, milk per 400 g). For the plate cost, beans are divided by 2.5 so rice, beans and garri are all per kg';
