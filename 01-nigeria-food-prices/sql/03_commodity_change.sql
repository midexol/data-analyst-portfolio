-- 03_commodity_change.sql
-- For each food: price in Jan 2023, its peak since then, and where it is now (Jul 2026).
WITH since_2023 AS (
    SELECT * FROM national_long WHERE month >= DATE '2023-01-01'
),
peaks AS (
    -- the month each food hit its highest price (the earliest one, if it hit it twice)
    SELECT food, month AS peak_month
    FROM (
        SELECT food, month, row_number() OVER (PARTITION BY food ORDER BY price DESC, month) AS rn
        FROM since_2023
    ) AS ranked
    WHERE rn = 1
),
per_food AS (
    SELECT
        s.food,
        max(CASE WHEN s.month = DATE '2023-01-01' THEN s.price END)  AS jan_2023,
        max(s.price)                                                 AS peak,
        max(p.peak_month)                                            AS peak_month,
        max(CASE WHEN s.month = DATE '2026-07-01' THEN s.price END)  AS jul_2026
    FROM since_2023 s
    JOIN peaks p ON p.food = s.food
    GROUP BY s.food
)
SELECT
    f.label                                                  AS food,
    p.food                                                   AS `column`,
    f.unit,
    CAST(round(jan_2023) AS SIGNED)                          AS price_jan_2023,
    CAST(round(peak) AS SIGNED)                              AS peak_price,
    DATE_FORMAT(peak_month, '%Y-%m')                         AS peak_month,
    CAST(round(jul_2026) AS SIGNED)                          AS price_jul_2026,
    CAST(round(100 * (peak / jan_2023 - 1)) AS SIGNED)       AS rise_to_peak_pct,
    CAST(round(100 * (jul_2026 / peak - 1)) AS SIGNED)       AS peak_to_now_pct,
    CAST(round(100 * (jul_2026 / jan_2023 - 1)) AS SIGNED)   AS jan_2023_to_now_pct
FROM per_food p
JOIN foods f ON f.food = p.food
ORDER BY jul_2026 / peak, f.label;
