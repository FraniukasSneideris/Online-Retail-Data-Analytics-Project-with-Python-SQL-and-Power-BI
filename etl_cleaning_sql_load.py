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
