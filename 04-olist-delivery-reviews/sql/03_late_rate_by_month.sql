-- 03_late_rate_by_month.sql
-- Share of orders delivered after the promised date, by purchase month.
SELECT
    CAST(DATE_FORMAT(purchased_at, '%Y-%m-01') AS DATE) AS month,
    count(*)                                          AS orders,
    round(100.0 * avg(is_late * 1e0), 1)               AS pct_late,
    round(avg(delivery_days * 1e0), 1)                      AS avg_delivery_days,
    round(avg(review_score * 1e0), 2)                       AS avg_review
FROM fct_orders
GROUP BY 1
ORDER BY 1;
