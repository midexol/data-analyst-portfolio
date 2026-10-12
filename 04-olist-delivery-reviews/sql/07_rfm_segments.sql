-- 07_rfm_segments.sql
-- Recency / Frequency / Monetary segments per unique customer.
-- Reference date = day after the last purchase in scope.
WITH ref AS (SELECT max(purchased_at) + INTERVAL 1 DAY AS ref_date FROM fct_orders),
cust AS (
    SELECT
        customer_unique_id,
        date_diff('day', max(purchased_at), (SELECT ref_date FROM ref)) AS recency_days,
        count(*)                                                         AS frequency,
        sum(items_value + freight_value)                                 AS monetary
    FROM fct_orders
    GROUP BY 1
),
scored AS (
    SELECT *,
           ntile(4) OVER (ORDER BY recency_days DESC, customer_unique_id) AS r_score,   -- 4 = most recent
           ntile(4) OVER (ORDER BY monetary, customer_unique_id)              AS m_score    -- 4 = biggest spend
    FROM cust
),
labelled AS (
    SELECT *,
        CASE
            WHEN frequency >= 2 AND r_score >= 3              THEN '1 · Loyal (repeat, recent)'
            WHEN frequency >= 2                               THEN '2 · Lapsed repeat buyers'
            WHEN m_score = 4 AND r_score >= 3                 THEN '3 · Recent big spenders'
            WHEN m_score = 4                                  THEN '4 · Lapsed big spenders'
            WHEN r_score >= 3                                 THEN '5 · Recent one-timers'
            ELSE                                                   '6 · Lapsed one-timers'
        END AS segment
    FROM scored
)
SELECT
    segment,
    count(*)                                               AS customers,
    round(100.0 * count(*) / sum(count(*)) OVER (), 1)     AS pct_customers,
    round(sum(monetary), 0)                                AS revenue_brl,
    round(100.0 * sum(monetary) / sum(sum(monetary)) OVER (), 1) AS pct_revenue,
    round(avg(monetary), 0)                                AS avg_spend_brl,
    round(avg(recency_days), 0)                            AS avg_recency_days
FROM labelled
GROUP BY segment
ORDER BY segment;
