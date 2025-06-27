# Online-Retail-Data-Analytics-Project-with-Python-SQL-and-Power-BI
![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Introduction

This project explores a full data pipeline using **Python**, **SQL**, and **Power BI**, starting from raw data and ending with an interactive dashboard.  
The goal was to generate insights on customer behavior, sales performance, and product returns using a combination of data analytics and data visualization techniques.

### Why these tools?

- **Python**: for data extraction, cleaning, and transformation.
- **SQL**: for querying, and preparing structured datasets.
- **Power BI**: for building a dynamic interactive dashboard to share insights.

While all data cleaning and transformation could have been done directly in Power BI, I chose to use Python and SQL (on Jupyter sheets) to integrate different tools and techniques. This approach showcases a more complete and flexible data workflow.

The **dataset** used in this project is the [Online Retail dataset](https://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository.
This dataset is comprised of **one excel file containing two sheets**: Year 2009-2010 and Year 2010-2011.
![image](https://github.com/user-attachments/assets/6a8d4ee4-9a59-4f39-ba62-9b3113f91423)

As it will be showed below, **these two sheets were combined, cleaned and saved using Python**. Then the **cleaned data was manipulated using SQL** in Python-script environment. And, finally, a **Dashboard was built using Power BI** with the manipulated data. 

*Please note*: the raw files were not included in the repository, because they were too heavy to load into GitHub.

---

## Part 1: ETL & Data Cleaning in Python
``` python
import pandas as pd
import sqlite3

# Read both sheets
df1 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2009-2010")
df2 = pd.read_excel("online_retail_II.xlsx", sheet_name="Year 2010-2011")

# Combine both sheets
df_comb = pd.concat([df1, df2], ignore_index=True)

## CLEANING
# Drop NaNs and make a deep copy to avoid SettingWithCopyWarning
df_nonan = df_comb.dropna().copy()

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

- Loading the raw CSV (both sheets)
- Combining sheets
- Handling missing values and duplicates
- Creating new date-based columns
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
           quantity * price AS total_revenue,
           invoicedate
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
           quantity * price AS total_returns_value,
           invoicedate
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

## Dashboard (Power BI)
### Dashboard Theme Rationale
To provide flexibility and enhance user experience, I’ve designed **two versions of the dashboard** using Power BI: one in a **light theme**, and one in a **dark theme**.

I genuinely like both — and I believe each has its own strengths, depending on the **audience**, the **context**, or even the **time of day** they’re being used.

![thumbnail](https://github.com/user-attachments/assets/29d6cfba-f979-4120-87cf-a49556f1c655)

- **Light Version**  
  Ideal for executive presentations, printed reports, and daytime reviews.  
  It offers a clean, minimal aesthetic that works well for clarity and formal communication.

- **Dark Version**  
  Designed with modern usability in mind — great for internal teams, large display screens, or evening usage.  
  It enhances contrast and helps data patterns pop visually.

By presenting both, the goal is to give users the option to choose the experience that best fits their needs — whether it’s clarity in the boardroom or focus during deep-dive analytics.

**Dashboard Walkthrough**: https://www.youtube.com/watch?v=tJZT9xYB1fI&t=5s

**Dashboard General Look (with music, no explanation)**: https://www.youtube.com/watch?v=LHLmKRj6i0M

The Power BI dashboard brings together insights generated in the previous steps and provides an interactive view into sales trends, customer behavior, and returns.

---

## DAX Measures

Key measures used in the dashboard include:
```dax
Total Revenue = SUM(sales_summary[total_revenue])

Total Quantity Sold = SUM(sales_summary[total_quantity])

Total Invoices = DISTINCTCOUNT('sales_summary'[invoice])

Revenue per Costumer = [Total Revenue]/[Total Costumers]

Average Order Value = [Total Revenue] / [Total Invoices]

Total Returns Value = SUM(returns_summary[total_returns_value])

Total Returns Count = COUNT(returns_summary[total_returns_quantity])

Returns Percentage = DIVIDE([Total Returns Value], [Total Revenue])

Products Count = COUNT(products_by_quantity[total_quantity])

Revenue per Product = DIVIDE([Total Revenue], [Products Count])

Number of Costumers = DISTINCTCOUNT(customer_activity[customer_id])
```

## DAX Calculated Columns
I created one calculated column (Costumer Type) specifically for the costumer_activity table, to classify costumers according to the amount of months they were active. Costumers are classified as **"Active"**, **"Normal"** or **"Inactive"**. This column becomes specially useful when using it as a slicer.
The formula is:
```dax
Customer Type = 
IF(
    [active_months] <= 2, 
    "Inactive", 
    IF(
        [active_months] <= 5, 
        "Normal", 
        "Active"
    )
)  
```
## Explanation for Each Visual in the Dashboard

Each visual on the dashboard is backed by specific insights and business logic, including:

### Key Performance Indicators
The upper pannel of the Dashboard displays the main KPIs, listed below:
- Total Revenue
- Total Quantity Sold
- Revenue per Costumer 
- Returns Percentage
- Total Returns Count
- Total Returns Value

The four KPIs in the middle have toltips, as follows:
- Total Quantity Sold over time (line chart)
- Revenue per Costumer over time (line chart)
- Total Returns Value and Total Revenue by Week (stacked area chart)
- Total Returns Count over time (line chart)

### Total Revenue over time
Line chart displaying Total Revenue measure by month and year.

### Customer insights 
Table chart displaying Customer, Country, Active Months, Customer Type, Average Spent and Total Revenue.

### Returns Section
Comprised of:
- Total Returns Value over time: line chart displaying Total Returns Value by month and year
- Returns in USD by Country: treemap displaying the total returns in USD by Country
- Revenue vs Returns in USD by Product: line and stacked column chart displaying Total Revenue (columns), Return Count (line) by Product (X axis).

### Number of Customers and Total Revenue by Active Months
Line and stacked column chart showing how customer loyalty, measured by the number of active months, relates to transaction volume (invoices) and total revenue, helping to identify how more loyal customers contribute to overall sales.

### AOV and Average Price over time
Line chart showing Average Order Price and Average price by week, helping identify trends, peaks, or seasonal shifts in customer spending behavior.

### Slicers
Affecting all visuals, filters the data by:
- Costumer Type
- Year
- Country

*Detailed breakdowns included in the video.*

---
## Conclusions

### Final Project Reflections

This end-to-end analytics project showcases:

- The value of combining multiple tools in a modern data workflow: Python/SQL for preprocessing, Power BI for visualization
- The importance of data cleaning and proper structure to ensure reliable insights
- How dashboards can turn raw numbers into interactive, accessible stories
- The impact of offering both light and dark themes to enhance usability across teams and settings

More than just a technical exercise, this project represents a real shift in how data can be communicated, making it accessible and insightful for a broader audience.

### Key Business Insights

#### Customer Engagement & Revenue
- Although the majority of customers were classified as "Inactive" or "Normal", the *"Active"* customers — just 27% of the total (1597 out of 5942) — were responsible for generating almost 80% of the total revenue ($13.37M out of $17.37M). This reflects a classic **Pareto Principle** (also known as the 80/20 rule), where a small share of customers drives the majority of business results. This is a very valuable insight, as the client can now focus its marketing or loyalty programs on retaining these high-value customers.
- There is a strong correlation between customer activity and revenue: the more active the customer, the higher their contribution to revenue.

#### Returns & Risk
- Inactive customers accounted for the highest return rates, but overall returns remained under 20%, indicating relatively healthy customer satisfaction.
- The United Kingdom showed the highest total revenue of all the countries at $14M.
- The United Kingdom also showed the highest return value ($906.7K), likely due to its larger customer base.

#### Product & Pricing Trends
- "Regency Cakestand 3 Tier" was the top-selling product, with over $277K in revenue.
- The average price of products stayed relatively stable throughout the year, but the Average Order Value (AOV) showed seasonal peaks, likely driven by multi-item purchases.
- Countries like the United Kingdom displayed large fluctuations in average price, suggesting pricing variation across customer segments.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

