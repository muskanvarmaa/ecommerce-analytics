import sqlite3
import pandas as pd

conn = sqlite3.connect("ecommerce.db")

with open("sql/top_products.sql") as f:
    query = f.read()

df = pd.read_sql_query(query, conn)

print(df)
conn.close()