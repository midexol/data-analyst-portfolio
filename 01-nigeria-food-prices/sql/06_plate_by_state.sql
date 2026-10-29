-- 06_plate_by_state.sql
-- Same plate, by state, July 2026 (median across that state's markets).
-- Most states only have 1-2 markets, so treat these as rough.
-- MySQL has no median(), so it's the middle market by price, or the average of the middle two.
WITH jul AS (
    SELECT state, market, plate_ngn
    FROM prices
    WHERE is_real_market AND month = DATE '2026-07-01'
),
ordered AS (
    SELECT state, plate_ngn,
           row_number() OVER (PARTITION BY state ORDER BY plate_ngn) AS rn,
           count(*) OVER (PARTITION BY state)                        AS n
    FROM jul
    WHERE plate_ngn IS NOT NULL
),
medians AS (
    SELECT state, avg(plate_ngn) AS median_plate
    FROM ordered
    WHERE rn IN (FLOOR((n + 1) / 2), CEIL((n + 1) / 2))
    GROUP BY state
)
SELECT
    j.state,
    count(DISTINCT j.market)                        AS markets,
    CAST(round(max(m.median_plate)) AS SIGNED)      AS plate_ngn
FROM jul j
LEFT JOIN medians m ON m.state = j.state
GROUP BY j.state
ORDER BY plate_ngn DESC;
