-- 04_late_rate_by_state.sql
-- Where in Brazil late deliveries concentrate (states with 500+ orders).
SELECT
    customer_state,
    count(*)                                AS orders,
    round(100.0 * avg(is_late * 1e0), 1)     AS pct_late,
    round(avg(delivery_days * 1e0), 1)            AS avg_delivery_days,
    round(avg(review_score * 1e0), 2)             AS avg_review
FROM fct_orders
GROUP BY 1
HAVING count(*) >= 500
ORDER BY pct_late DESC;
