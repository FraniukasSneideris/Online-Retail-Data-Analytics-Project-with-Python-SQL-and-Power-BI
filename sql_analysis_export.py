# SQL ANALYSIS + PREP FOR POWER BI

import sqlite3
import pandas as pd

conn = sqlite3.connect("online_retail_clean.db")

# sales_sumamry df
query1 = """
    SELECT customer_id,
           invoice,
           description,
           country,
           year,
           month,
           week,
           price,
           quantity AS total_quantity,
           quantity * price AS total_revenue
    FROM retail_data
    WHERE quantity > 0
"""
sales_summary = pd.read_sql_query(query1, conn)

# products_by_quantity df
query2 = """
    SELECT invoice,
           stockcode,
           description,
           quantity AS total_quantity
    FROM retail_data
    WHERE quantity > 0
    ORDER BY total_quantity DESC
"""
products_by_quantity = pd.read_sql_query(query2, conn)

# customer_activity df
query3 = """
    SELECT customer_id,
           invoice,
           quantity * price AS total_spent,
           MAX(invoicedate) AS last_purchase_date,
           COUNT(DISTINCT year || '-' || month) AS active_months
    FROM retail_data
    GROUP BY customer_id
    ORDER BY total_spent DESC
"""
customer_activity = pd.read_sql_query(query3, conn)

# returns_summary df
query4 = """
    SELECT customer_id,
           invoice,
           country,
           year,
           month,
           week,
           stockcode,
           description,
           price,
           quantity AS total_returns_quantity,
           quantity * price AS total_returns_value
    FROM retail_data
    WHERE quantity < 0
"""
returns_summary = pd.read_sql_query(query4, conn)

conn.close()

# Save to CSV
sales_summary.to_csv("sales_summary.csv", index=False)
products_by_quantity.to_csv("products_by_quantity.csv", index=False)
customer_activity.to_csv("customer_activity.csv", index=False)
returns_summary.to_csv("returns_summary.csv", index=False)
