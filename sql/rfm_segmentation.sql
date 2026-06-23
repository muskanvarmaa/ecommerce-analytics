WITH rfm_raw AS (
    SELECT
        c.customer_unique_id,
        CAST(JULIANDAY('now') - JULIANDAY(MAX(o.order_purchase_timestamp)) AS INTEGER) AS recency_days,
        COUNT(o.order_id) AS frequency,
        ROUND(SUM(op.payment_value),2) AS monetary
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC)  AS m_score
    FROM rfm_raw
),
rfm_segmented AS (
    SELECT *,
        CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score < 3  THEN 'Recent Customers'
            WHEN r_score < 3  AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential Loyalists'
        END AS segment
    FROM rfm_scored
)
SELECT segment, COUNT(*) AS customer_count
FROM rfm_segmented
GROUP BY segment
ORDER BY customer_count DESC;