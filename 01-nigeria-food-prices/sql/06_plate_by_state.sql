-- 06_plate_by_state.sql
-- Same plate, by state, July 2026 (median across that state's markets).
-- Most states only have 1-2 markets, so treat these as rough.
SELECT
    state,
    count(DISTINCT market)       AS markets,
    CAST(round(median(plate_ngn)) AS INTEGER)     AS plate_ngn
FROM prices
WHERE is_real_market AND month = DATE '2026-07-01'
GROUP BY state
ORDER BY plate_ngn DESC;
