# 🛒 CartIQ — E-Commerce Sales & Customer Analytics

End-to-end data analytics project on the [Olist Brazilian E-Commerce dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) — 100k+ real orders across 9 tables.

## 🔧 Tech Stack
- **Python** — pandas, matplotlib, streamlit
- **SQL** — SQLite with advanced queries
- **Jupyter Notebook** — full EDA walkthrough

## 📊 What's Inside

| File | Description |
|------|-------------|
| `load_data.py` | ETL pipeline — loads 9 CSVs into SQLite |
| `revenue_trends.sql` | Monthly GMV + MoM growth using LAG() |
| `rfm_segmentation.sql` | Customer segmentation using NTILE() window functions |
| `top_products.sql` | Top categories by revenue — multi-table JOINs |
| `analysis.ipynb` | Full EDA with matplotlib visualizations |
| `app.py` | Interactive Streamlit dashboard |

## 🔑 Key SQL Concepts Used
`Window Functions (LAG, NTILE, ROW_NUMBER)` · `CTEs` · `Multi-table JOINs` · `CASE WHEN` · `DATE functions` · `Subqueries`

## 🚀 How to Run

```bash
# Install dependencies
pip install pandas matplotlib streamlit jupyter

# Load data into SQLite
python load_data.py

# Launch dashboard
streamlit run app.py
```

## 📈 Key Insights
- Revenue grew from **R$46K (Oct 2016)** to **R$1.1M/month (2018)**
- **Black Friday 2017** spike — 53% MoM growth
- **22,000+ customers** identified as "At Risk" via RFM segmentation
- **Health & Beauty** is the top revenue category at R$1.2M+

---
Built by [Muskan Varma](https://github.com/muskanvarmaa)
