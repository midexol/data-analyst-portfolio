-- 06_repeat_purchase.sql
-- Does a late FIRST delivery make a customer less likely to order again?
-- Only customers whose first order was before 2018-03-01 are included, so everyone
-- has at least 6 months in which a second order could appear.
WITH ranked AS (
    SELECT customer_unique_id, order_id, purchased_at, is_late, review_score,
           row_number() OVER (PARTITION BY customer_unique_id ORDER BY purchased_at, order_id) AS n
    FROM fct_orders
),
firsts AS (
    SELECT customer_unique_id, purchased_at AS first_at, is_late AS first_late,
           review_score AS first_review
    FROM ranked WHERE n = 1
),
repeaters AS (
    SELECT DISTINCT customer_unique_id FROM ranked WHERE n >= 2
)
SELECT
    CASE WHEN first_late THEN 'First order late' ELSE 'First order on time' END AS first_experience,
    count(*)                                                          AS customers,
    sum(CASE WHEN r.customer_unique_id IS NOT NULL THEN 1 ELSE 0 END) AS repeat_customers,
    round(100.0 * avg(CASE WHEN r.customer_unique_id IS NOT NULL THEN 1 ELSE 0 END), 2) AS pct_repeat
FROM firsts f
LEFT JOIN repeaters r USING (customer_unique_id)
WHERE first_at < TIMESTAMP '2018-03-01'
GROUP BY 1
ORDER BY 1;
