-- 02_delivery_vs_reviews.sql
-- How review scores fall as deliveries slip past the promised date.
SELECT
    delay_bucket,
    count(*)                                                         AS orders,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1)               AS pct_of_orders,
    round(avg(review_score), 2)                                      AS avg_review,
    round(100.0 * avg(CASE WHEN review_score <= 2 THEN 1 ELSE 0 END), 1) AS pct_1_2_stars,
    round(100.0 * avg(CASE WHEN review_score = 5 THEN 1 ELSE 0 END), 1)  AS pct_5_stars
FROM fct_orders
WHERE review_score IS NOT NULL
GROUP BY delay_bucket
ORDER BY delay_bucket;
