-- 05_plate_by_zone.sql
-- Cost of 1 kg each of rice, beans and garri in each geopolitical zone:
-- Jan 2023, the peak month (highest average across zones), and Jul 2026.
WITH zones AS (
    SELECT market AS zone, month, plate_ngn
    FROM prices
    WHERE state = 'Geopolitical Zone' AND month >= DATE '2023-01-01'
),
peak AS (
    SELECT month AS peak_month
    FROM zones
    GROUP BY month
    ORDER BY avg(plate_ngn) DESC
    LIMIT 1
)
SELECT
    zone,
    CAST(round(max(CASE WHEN month = DATE '2023-01-01' THEN plate_ngn END)) AS SIGNED)          AS plate_jan_2023,
    DATE_FORMAT((SELECT peak_month FROM peak), '%Y-%m')                                         AS peak_month,
    CAST(round(max(CASE WHEN month = (SELECT peak_month FROM peak) THEN plate_ngn END)) AS SIGNED) AS plate_peak,
    CAST(round(max(CASE WHEN month = DATE '2026-07-01' THEN plate_ngn END)) AS SIGNED)          AS plate_jul_2026
FROM zones
GROUP BY zone
ORDER BY plate_jul_2026 DESC;
