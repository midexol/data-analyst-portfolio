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
    CAST(round(max(plate_ngn) FILTER (WHERE month = DATE '2023-01-01')) AS INTEGER)            AS plate_jan_2023,
    strftime((SELECT peak_month FROM peak), '%Y-%m')                          AS peak_month,
    CAST(round(max(plate_ngn) FILTER (WHERE month = (SELECT peak_month FROM peak))) AS INTEGER) AS plate_peak,
    CAST(round(max(plate_ngn) FILTER (WHERE month = DATE '2026-07-01')) AS INTEGER)            AS plate_jul_2026
FROM zones
GROUP BY zone
ORDER BY plate_jul_2026 DESC;
