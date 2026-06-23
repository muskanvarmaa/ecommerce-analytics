import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(page_title="E-Commerce Analytics", layout="wide", page_icon="🛒")

st.markdown("""
    <style>
    .main { background-color: #0f1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #252a3d);
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid #4f8ef7;
        margin-bottom: 10px;
    }
    .metric-value { font-size: 32px; font-weight: 700; color: #4f8ef7; }
    .metric-label { font-size: 13px; color: #8892a4; margin-bottom: 4px; }
    .section-title { font-size: 20px; font-weight: 600; color: #ffffff; margin: 20px 0 10px; }
    </style>
""", unsafe_allow_html=True)

# Dark style for matplotlib
plt.style.use("dark_background")
BLUE = "#4f8ef7"
CORAL = "#ff6b6b"
GREEN = "#2ecc71"
PURPLE = "#a29bfe"
GRAY = "#636e72"

conn = sqlite3.connect("ecommerce.db")

# Header
st.markdown("<h1 style='color:#4f8ef7;'>🛒 E-Commerce Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='color:#8892a4;'>Olist Brazilian E-Commerce · 100k+ Orders · Python + SQL</p>", unsafe_allow_html=True)
st.divider()

#  KPI Cards 
total_orders = pd.read_sql_query("SELECT COUNT(DISTINCT order_id) AS n FROM orders WHERE order_status='delivered'", conn).iloc[0,0]
total_revenue = pd.read_sql_query("SELECT ROUND(SUM(payment_value),2) AS n FROM order_payments", conn).iloc[0,0]
total_customers = pd.read_sql_query("SELECT COUNT(DISTINCT customer_unique_id) AS n FROM customers", conn).iloc[0,0]
avg_order = total_revenue / total_orders

col1, col2, col3, col4 = st.columns(4)
col1.metric("🧾 Total Orders", f"{total_orders:,}", "delivered")
col2.metric("💰 Total Revenue", f"R${total_revenue/1e6:.2f}M", "+GMV")
col3.metric("👥 Unique Customers", f"{total_customers:,}")
col4.metric("🛍️ Avg Order Value", f"R${avg_order:.0f}")

st.divider()

#  Revenue Trend 
st.markdown("<div class='section-title'>📈 Monthly Revenue Trend</div>", unsafe_allow_html=True)

rev_df = pd.read_sql_query("""
    WITH monthly AS (
        SELECT STRFTIME('%Y-%m', o.order_purchase_timestamp) AS month,
               ROUND(SUM(op.payment_value)/1000, 1) AS gmv_k
        FROM orders o JOIN order_payments op ON o.order_id = op.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY month ORDER BY month
    )
    SELECT * FROM monthly
""", conn)

fig, ax = plt.subplots(figsize=(14, 4))
fig.patch.set_facecolor("#0f1117")
ax.set_facecolor("#0f1117")
colors = [CORAL if v == rev_df["gmv_k"].max() else BLUE for v in rev_df["gmv_k"]]
bars = ax.bar(rev_df["month"], rev_df["gmv_k"], color=colors, width=0.7, edgecolor="none")
ax.plot(rev_df["month"], rev_df["gmv_k"], color=GREEN, linewidth=1.5, alpha=0.6, marker="o", markersize=3)
ax.set_ylabel("GMV (BRL thousands)", color="#8892a4", fontsize=11)
ax.tick_params(colors="#8892a4")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#2d3148")
ax.spines["bottom"].set_color("#2d3148")
plt.xticks(rotation=45, ha="right", fontsize=9)
ax.annotate("🔥 Black Friday", xy=(12, rev_df["gmv_k"].max()),
            xytext=(14, rev_df["gmv_k"].max() - 100),
            color=CORAL, fontsize=9,
            arrowprops=dict(arrowstyle="->", color=CORAL))
plt.tight_layout()
st.pyplot(fig)

st.divider()

#  RFM + Categories 
col1, col2 = st.columns(2)

with col1:
    st.markdown("<div class='section-title'>👥 Customer Segments (RFM)</div>", unsafe_allow_html=True)
    rfm_df = pd.read_sql_query("""
        WITH last_order AS (SELECT MAX(order_purchase_timestamp) AS max_date FROM orders),
        rfm_raw AS (
            SELECT c.customer_unique_id,
                CAST(JULIANDAY((SELECT max_date FROM last_order))
                     - JULIANDAY(MAX(o.order_purchase_timestamp)) AS INTEGER) AS recency_days,
                COUNT(DISTINCT o.order_id) AS frequency,
                ROUND(SUM(op.payment_value), 2) AS monetary
            FROM customers c
            JOIN orders o ON c.customer_id = o.customer_id
            JOIN order_payments op ON o.order_id = op.order_id
            WHERE o.order_status = 'delivered'
            GROUP BY c.customer_unique_id
        ),
        rfm_scored AS (
            SELECT *,
                NTILE(5) OVER (ORDER BY recency_days ASC) AS r_score,
                NTILE(5) OVER (ORDER BY frequency DESC) AS f_score,
                NTILE(5) OVER (ORDER BY monetary DESC) AS m_score
            FROM rfm_raw
        )
        SELECT CASE
            WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
            WHEN r_score >= 4 AND f_score < 3  THEN 'Recent Customers'
            WHEN r_score < 3  AND f_score >= 3 THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2 THEN 'Lost'
            ELSE 'Potential Loyalists'
        END AS segment, COUNT(*) AS customers
        FROM rfm_scored GROUP BY segment ORDER BY customers ASC
    """, conn)

    seg_colors = {
        "Champions": GREEN, "Loyal Customers": BLUE,
        "Recent Customers": PURPLE, "Potential Loyalists": "#fdcb6e",
        "At Risk": CORAL, "Lost": GRAY
    }
    colors = [seg_colors.get(s, BLUE) for s in rfm_df["segment"]]

    fig2, ax2 = plt.subplots(figsize=(7, 5))
    fig2.patch.set_facecolor("#0f1117")
    ax2.set_facecolor("#0f1117")
    bars = ax2.barh(rfm_df["segment"], rfm_df["customers"], color=colors, edgecolor="none", height=0.6)
    ax2.bar_label(bars, padding=4, color="#8892a4", fontsize=9)
    ax2.tick_params(colors="#8892a4")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_color("#2d3148")
    ax2.spines["bottom"].set_color("#2d3148")
    ax2.set_xlabel("Number of Customers", color="#8892a4")
    plt.tight_layout()
    st.pyplot(fig2)

with col2:
    st.markdown("<div class='section-title'>🏆 Top Categories by Revenue</div>", unsafe_allow_html=True)
    cat_df = pd.read_sql_query("""
        SELECT COALESCE(t.product_category_name_english,
                        p.product_category_name, 'Unknown') AS category,
               ROUND(SUM(oi.price)/1000, 1) AS revenue_k
        FROM order_items oi
        JOIN products p ON oi.product_id = p.product_id
        LEFT JOIN product_category_name_translation t
               ON p.product_category_name = t.product_category_name
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status = 'delivered'
        GROUP BY category ORDER BY revenue_k DESC LIMIT 8
    """, conn)

    fig3, ax3 = plt.subplots(figsize=(7, 5))
    fig3.patch.set_facecolor("#0f1117")
    ax3.set_facecolor("#0f1117")
    grad_colors = [BLUE, "#5b9cf7", "#6aaaf7", "#79b8f7",
                   "#88c6f7", "#97d4f7", "#a6e2f7", "#b5f0f7"]
    bars3 = ax3.barh(cat_df["category"], cat_df["revenue_k"],
                     color=grad_colors, edgecolor="none", height=0.6)
    ax3.bar_label(bars3, padding=4, fmt="R$%.0fK", color="#8892a4", fontsize=9)
    ax3.invert_yaxis()
    ax3.tick_params(colors="#8892a4")
    ax3.spines["top"].set_visible(False)
    ax3.spines["right"].set_visible(False)
    ax3.spines["left"].set_color("#2d3148")
    ax3.spines["bottom"].set_color("#2d3148")
    ax3.set_xlabel("Revenue (BRL thousands)", color="#8892a4")
    plt.tight_layout()
    st.pyplot(fig3)

conn.close()
st.markdown("<p style='text-align:center; color:#8892a4; font-size:12px; margin-top:40px;'>Built by Muskan Varma · Python + SQL + Streamlit</p>", unsafe_allow_html=True)