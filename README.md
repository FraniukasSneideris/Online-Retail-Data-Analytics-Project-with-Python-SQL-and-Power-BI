# Online-Retail-Data-Analytics-Project-with-Python-SQL-and-Power-BI

## Introduction

This project explores a full data pipeline using **Python**, **SQL**, and **Power BI**, starting from raw data and ending with an interactive dashboard.  
The goal was to generate insights on customer behavior, sales performance, and product returns using a combination of data analytics and data visualization techniques.

### Why these tools?

- **Python**: for data extraction, cleaning, and transformation.
- **SQL**: for querying, aggregating, and preparing structured datasets.
- **Power BI**: for building a dynamic interactive dashboard to share insights.

While all data cleaning and transformation could have been done directly in Power BI, I chose to use Python and SQL to integrate different tools and techniques. This approach showcases a more complete and flexible data workflow.

The **dataset** used in this project is the [Online Retail dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository.

---

## Part 1: ETL & Data Cleaning in Python
``` python
# ETL PHASE - DATA PREPARATION

import pandas as pd
import sqlite3

# Load CSV
df = pd.read_csv("online_retail_2010-2011.csv")

## CLEANING
# Drop NaNs and make a deep copy to avoid SettingWithCopyWarning
df_nonan = df.dropna().copy()

# Drop duplicates
df_clean = df_nonan.drop_duplicates().copy()

# Convert InvoiceDate to datetime
df_clean["InvoiceDate"] = pd.to_datetime(df_clean["InvoiceDate"], errors="coerce")

# Create new columns extracting the year, month, and others from InvoiceDate
df_clean["Year"] = df_clean["InvoiceDate"].dt.year
df_clean["Month"] = df_clean["InvoiceDate"].dt.month
df_clean["DayOfWeek"] = df_clean["InvoiceDate"].dt.day_name()
df_clean['Week'] = df_clean['InvoiceDate'].dt.isocalendar().week
df_clean['Quarter'] = df_clean['InvoiceDate'].dt.quarter

# Convert Customer ID to int
df_clean["Customer ID"] = df_clean["Customer ID"].astype("int")

# Renaming columns for SQL friendliness
df_clean.columns = df_clean.columns.str.lower().str.replace(" ", "_")

## Save with SQLite
conn = sqlite3.connect("online_retail_clean.db")
df_clean.to_sql("retail_data", conn, index=False, if_exists="replace")
conn.close()
```

**Overview of the steps:**

- Loading the raw CSV
- Handling missing values and duplicates
- Creating date-based features (e.g., year, month, week, weekday, quarter)
- Renaming columns for SQL compatibility
- Saving the cleaned dataset to a local SQLite database

---

## Part 2: SQL Analysis in Python Script Environment
``` python
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
```

**Overview of SQL queries and exports:**

- `sales_summary`: Clean sales transactions and revenue calculations  
- `products_by_quantity`: Products overview (excluding returns) 
- `customer_activity`: Lifetime value and engagement by customer  
- `returns_summary`: Product return patterns and total return values  

All queries are executed using `sqlite3` and exported to CSV for use in Power BI.

---

## 📊 Dashboard (Power BI)

🎥 **Dashboard Walkthrough**: [Link to Video – To Be Added]

The Power BI dashboard brings together insights generated in the previous steps and provides an interactive view into sales trends, customer behavior, and returns.

---

## 📏 DAX Measures

Key measures used in the dashboard include (but are not limited to):

- Total Revenue  
- Total Returns  
- Net Revenue  
- Average Order Value  
- Monthly Active Customers  
- Top Products (by revenue and quantity)

---

## 📈 Visual Explanations

Each visual on the dashboard is backed by specific insights and business logic, including:

- Sales trend over time  
- Customer segmentation  
- Product performance  
- Return rates and patterns  

*Detailed breakdowns included in the video and Power BI section.*

---

## ✅ Conclusion

This end-to-end analytics project showcases:

- The value of combining multiple tools in a modern data workflow  
- The importance of data cleaning and structure in analysis  
- How dashboards can bring raw numbers to life with interactivity  

---

## 🧑‍💻 Author

Made with ❤️ and Python  
by [Your Name]

---

## 📜 License

Distributed under the MIT License.
