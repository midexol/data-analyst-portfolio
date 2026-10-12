-- 03_late_rate_by_month.sql
-- Share of orders delivered after the promised date, by purchase month.
SELECT
    date_trunc('month', purchased_at)                 AS month,
    count(*)                                          AS orders,
    round(100.0 * avg(is_late::INT), 1)               AS pct_late,
    round(avg(delivery_days), 1)                      AS avg_delivery_days,
    round(avg(review_score), 2)                       AS avg_review
FROM fct_orders
GROUP BY 1
ORDER BY 1;
