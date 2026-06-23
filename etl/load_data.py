import pandas as pd
import sqlite3
import os
files = {
    "customers": 'data\olist_customers_dataset.csv',
    "orders": 'data\olist_orders_dataset.csv', 
    "order_items": 'data\olist_order_items_dataset.csv',
    "order_payments": 'data\olist_order_payments_dataset.csv',
    "order_reviews": 'data\olist_order_reviews_dataset.csv',
    "products": 'data\olist_products_dataset.csv',
    "sellers": 'data\olist_sellers_dataset.csv',
    "geolocation": 'data\olist_geolocation_dataset.csv',
    "product_category_name_translation": 'data\product_category_name_translation.csv',
}
tables = {}
for table_name, filename in files.items():
    df = pd.read_csv(filename)
    print(table_name, df.shape)
    tables[table_name] = df

tables["orders"]["order_purchase_timestamp"] = pd.to_datetime(tables["orders"]["order_purchase_timestamp"])
  
conn = sqlite3.connect("ecommerce.db")
for table_name, df in tables.items():
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {table_name} into database")

conn.close()
print("Done! Database created.")