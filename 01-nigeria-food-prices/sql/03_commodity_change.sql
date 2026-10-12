-- 03_commodity_change.sql
-- For each food: price in Jan 2023, its peak since then, and where it is now (Jul 2026).
WITH since_2023 AS (
    SELECT * FROM national_long WHERE month >= DATE '2023-01-01'
),
per_food AS (
    SELECT
        food,
        max(price) FILTER (WHERE month = DATE '2023-01-01')  AS jan_2023,
        max(price)                                           AS peak,
        arg_max(month, price)                                AS peak_month,
        max(price) FILTER (WHERE month = DATE '2026-07-01')  AS jul_2026
    FROM since_2023
    GROUP BY food
)
SELECT
    f.label                                         AS food,
    p.food                                          AS "column",
    f.unit,
    CAST(round(jan_2023) AS INTEGER)                                 AS price_jan_2023,
    CAST(round(peak) AS INTEGER)                                     AS peak_price,
    strftime(peak_month, '%Y-%m')                   AS peak_month,
    CAST(round(jul_2026) AS INTEGER)                                 AS price_jul_2026,
    CAST(round(100 * (peak / jan_2023 - 1)) AS INTEGER)              AS rise_to_peak_pct,
    CAST(round(100 * (jul_2026 / peak - 1)) AS INTEGER)              AS peak_to_now_pct,
    CAST(round(100 * (jul_2026 / jan_2023 - 1)) AS INTEGER)          AS jan_2023_to_now_pct
FROM per_food p
JOIN foods f USING (food)
ORDER BY jul_2026 / peak, f.label;
