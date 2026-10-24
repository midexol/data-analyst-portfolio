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
        SELECT adm1_name, mkt_name, price_month FROM raw GROUP BY ALL HAVING count(*) > 1
    )
),
missing AS (
    -- estimated prices that are empty, across all 16 foods, inside the window I use
    SELECT
          count(*) FILTER (WHERE c_beans IS NULL) + count(*) FILTER (WHERE c_eggs IS NULL)
        + count(*) FILTER (WHERE c_fish IS NULL) + count(*) FILTER (WHERE c_gari_fao IS NULL)
        + count(*) FILTER (WHERE c_groundnuts IS NULL) + count(*) FILTER (WHERE c_maize_fao IS NULL)
        + count(*) FILTER (WHERE c_maize_flour IS NULL) + count(*) FILTER (WHERE c_meat_beef IS NULL)
        + count(*) FILTER (WHERE c_meat_goat IS NULL) + count(*) FILTER (WHERE c_milk IS NULL)
        + count(*) FILTER (WHERE c_millet IS NULL) + count(*) FILTER (WHERE c_onions IS NULL)
        + count(*) FILTER (WHERE c_rice IS NULL) + count(*) FILTER (WHERE c_rice_fao IS NULL)
        + count(*) FILTER (WHERE c_sorghum_fao IS NULL) + count(*) FILTER (WHERE c_yam IS NULL) AS n
    FROM in_window
    WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone')
),
collected AS (
    -- share of market prices that were actually collected, not estimated by the model
    SELECT round(100.0 * avg(
          (beans IS NOT NULL)::INT + (eggs IS NOT NULL)::INT + (fish IS NOT NULL)::INT
        + (gari_fao IS NOT NULL)::INT + (groundnuts IS NOT NULL)::INT + (maize_fao IS NOT NULL)::INT
        + (maize_flour IS NOT NULL)::INT + (meat_beef IS NOT NULL)::INT + (meat_goat IS NOT NULL)::INT
        + (milk IS NOT NULL)::INT + (millet IS NOT NULL)::INT + (onions IS NOT NULL)::INT
        + (rice IS NOT NULL)::INT + (rice_fao IS NOT NULL)::INT + (sorghum_fao IS NOT NULL)::INT
        + (yam IS NOT NULL)::INT) / 16, 1) AS pct
    FROM in_window
    WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone')
)
SELECT * FROM (VALUES
    (1, 'Start with the raw World Bank file',
        (SELECT count(*) FROM raw),
        (SELECT count(DISTINCT adm1_name || '|' || mkt_name) FROM raw) || ' price series, '
            || (SELECT count(DISTINCT price_month) FROM raw) || ' months (Jan 2007 to Aug 2026), 137 columns'),
    (2, 'Drop August 2026',
        (SELECT count(*) FROM raw WHERE price_month <= DATE '2026-07-01'),
        'The file says its last real survey was July 2026, so August is a forecast, not data'),
    (3, 'Keep January 2019 onward',
        (SELECT count(*) FROM in_window),
        'Earlier years are much thinner (under 10% of prices collected before 2017). 2019 also gives four full years before the 2023 jump to compare against'),
    (4, 'Check for duplicate market-months',
        (SELECT count(*) FROM in_window),
        (SELECT n FROM dupes) || ' duplicates found, nothing removed'),
    (5, 'Sort the rows into three kinds',
        (SELECT count(*) FROM in_window),
        (SELECT count(DISTINCT mkt_name) FROM in_window WHERE adm1_name NOT IN ('Market Average', 'Geopolitical Zone'))
            || ' real markets, 5 zone series, 1 national average. Nothing removed, they''re just used for different things'),
    (6, 'Fix two mislabelled markets',
        (SELECT count(*) FROM in_window),
        '"National Average" is really Abuja market and "Kano State (1)" is really Kano city market. Both have their own coordinates and collected prices, so I renamed their states to FCT and Kano and counted them as markets'),
    (7, 'Check for missing prices',
        (SELECT count(*) FROM in_window),
        (SELECT n FROM missing) || ' empty estimated prices in the window, so no filling needed'),
    (8, 'Note how much is estimated',
        (SELECT count(*) FROM in_window),
        'Only ' || (SELECT pct FROM collected) || '% of market prices since 2019 were actually collected. The rest are World Bank model estimates. Kept, but flagged in the write-up'),
    (9, 'Put prices on the same footing',
        (SELECT count(*) FROM in_window),
        'Each food has its own unit (beans per 2.5 kg, eggs per 30, milk per 400 g). For the plate cost, beans are divided by 2.5 so rice, beans and garri are all per kg')
) AS t(step, what_i_did, rows_after, why);
