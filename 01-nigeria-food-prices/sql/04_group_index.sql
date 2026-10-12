-- 04_group_index.sql
-- Grains vs protein: average of each food's price relative to Jan 2023 (= 100).
WITH base AS (
    SELECT food, price AS base_price FROM national_long WHERE month = DATE '2023-01-01'
),
indexed AS (
    SELECT n.month, f.food_group, 100 * n.price / b.base_price AS idx
    FROM national_long n
    JOIN base b USING (food)
    JOIN foods f USING (food)
    WHERE n.month >= DATE '2023-01-01' AND f.food_group IS NOT NULL
)
SELECT
    month                                                        AS date,
    round(avg(idx) FILTER (WHERE food_group = 'grains'), 1)      AS "Grains, beans and garri",
    round(avg(idx) FILTER (WHERE food_group = 'protein'), 1)     AS "Meat, eggs and milk"
FROM indexed
GROUP BY month
ORDER BY month;
