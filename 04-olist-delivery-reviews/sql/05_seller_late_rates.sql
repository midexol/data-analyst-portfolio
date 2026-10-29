-- 05_seller_late_rates.sql
-- Which sellers account for the most late orders.
-- An order with items from several sellers counts once for each seller.
WITH order_sellers AS (
    SELECT DISTINCT order_id, seller_id FROM raw_items
),
per_seller AS (
    SELECT
        os.seller_id,
        count(*)                          AS orders,
        sum(f.is_late)               AS late_orders,
        avg(f.review_score * 1e0)         AS avg_review
    FROM order_sellers os
    JOIN fct_orders f USING (order_id)
    GROUP BY os.seller_id
)
SELECT
    seller_id,
    orders,
    late_orders,
    round(100.0 * late_orders / orders, 1)                                  AS pct_late,
    round(CAST(avg_review AS DECIMAL(20, 6)), 2)                            AS avg_review,  -- exact decimal, so halves round up
    round(100.0 * late_orders / sum(late_orders) OVER (), 2)                AS pct_of_all_late,
    round(100.0 * sum(late_orders) OVER (ORDER BY late_orders DESC, seller_id
                                         ROWS UNBOUNDED PRECEDING)
          / sum(late_orders) OVER (), 1)                                    AS cumulative_pct_of_late
FROM per_seller
ORDER BY late_orders DESC, seller_id;
