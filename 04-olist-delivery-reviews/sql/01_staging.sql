-- 01_staging.sql
-- Builds clean, one-row-per-order tables from the raw Olist CSVs.
-- Scope: delivered orders purchased 2017-01-01 to 2018-08-31 (the months with full volume).

CREATE OR REPLACE TABLE stg_orders AS
SELECT
    o.order_id,
    o.customer_id,
    o.order_purchase_timestamp                         AS purchased_at,
    o.order_delivered_customer_date                    AS delivered_at,
    o.order_estimated_delivery_date                    AS estimated_at,
    date_diff('day', o.order_purchase_timestamp, o.order_delivered_customer_date)      AS delivery_days,
    -- days late vs the date promised at checkout (negative = early)
    date_diff('day', CAST(o.order_estimated_delivery_date AS DATE),
                     CAST(o.order_delivered_customer_date AS DATE))                    AS days_late
FROM raw_orders o
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_purchase_timestamp >= TIMESTAMP '2017-01-01'
  AND o.order_purchase_timestamp <  TIMESTAMP '2018-09-01';

-- A few orders have more than one review; keep the most recent answer.
CREATE OR REPLACE TABLE stg_reviews AS
SELECT order_id, review_score
FROM (
    SELECT order_id, review_score,
           row_number() OVER (PARTITION BY order_id
                              ORDER BY review_answer_timestamp DESC, review_creation_date DESC, review_id) AS rn
    FROM raw_reviews
)
WHERE rn = 1;

CREATE OR REPLACE TABLE stg_order_value AS
SELECT order_id,
       sum(price)          AS items_value,
       sum(freight_value)  AS freight_value,
       count(*)            AS n_items
FROM raw_items
GROUP BY order_id;

CREATE OR REPLACE TABLE fct_orders AS
SELECT
    s.*,
    c.customer_unique_id,
    c.customer_state,
    r.review_score,
    v.items_value,
    v.freight_value,
    v.n_items,
    CASE
        WHEN s.days_late <= 0  THEN '0 · On time or early'
        WHEN s.days_late <= 3  THEN '1 · 1-3 days late'
        WHEN s.days_late <= 7  THEN '2 · 4-7 days late'
        WHEN s.days_late <= 14 THEN '3 · 8-14 days late'
        ELSE                        '4 · 15+ days late'
    END                                   AS delay_bucket,
    (s.days_late > 0)                     AS is_late
FROM stg_orders s
JOIN raw_customers c USING (customer_id)
LEFT JOIN stg_reviews r USING (order_id)
LEFT JOIN stg_order_value v USING (order_id);
