WITH monthly AS (
    SELECT 
        STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month,
        COUNT(o.order_id) AS total_orders,
        ROUND(SUM(op.payment_value), 2) AS total_revenue
    FROM orders o
    JOIN order_payments op ON o.order_id = op.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY month
)
SELECT
    month,
    total_orders,
    total_revenue,
    ROUND(
        (total_revenue - LAG(total_revenue) OVER (ORDER BY month)) * 100.0
        / LAG(total_revenue) OVER (ORDER BY month), 2
    ) AS mom_growth_pct
FROM monthly
ORDER BY month;