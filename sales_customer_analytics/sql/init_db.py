"""
init_db.py
----------
Initializes SQLite database 'data/sales_analytics.db', creates relational tables
using schema.sql, and ingests cleaned data into normalized tables.
"""

import os
import sqlite3
import pandas as pd


def initialize_database(db_path: str, schema_path: str, clean_csv_path: str):
    """Sets up the SQLite database and loads normalized tables."""
    print("=" * 60)
    print("INITIALIZING SQLITE ANALYTICS DATABASE")
    print("=" * 60)

    if not os.path.exists(clean_csv_path):
        raise FileNotFoundError(f"Clean CSV file not found at: {clean_csv_path}")

    # Ensure target directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # Connect to SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Read and execute schema
    print(f"[Step 1] Applying schema from: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Ingest clean CSV
    print(f"[Step 2] Ingesting cleaned data from: {clean_csv_path}")
    df = pd.read_csv(clean_csv_path)

    # 1. Populate Customers Table (Unique records)
    customers_df = df[[
        "customer_id", "customer_name", "segment", "country", "region", "state", "city"
    ]].drop_duplicates(subset=["customer_id"])
    customers_df.to_sql("customers", conn, if_exists="append", index=False)
    print(f"  -> Inserted {len(customers_df):,} records into 'customers' table.")

    # 2. Populate Products Table (Unique records)
    products_df = df[[
        "product_id", "product_name", "category", "sub_category", "unit_cost", "unit_price"
    ]].drop_duplicates(subset=["product_id"])
    products_df.to_sql("products", conn, if_exists="append", index=False)
    print(f"  -> Inserted {len(products_df):,} records into 'products' table.")

    # 3. Populate Sales Transactions Fact Table
    transactions_cols = [
        "order_id", "order_date", "ship_date", "ship_mode", "customer_id", "product_id",
        "quantity", "discount", "sales_revenue", "cogs", "profit", "profit_margin",
        "order_status", "payment_method", "order_year", "order_quarter", "order_month", "order_day_of_week"
    ]
    transactions_df = df[transactions_cols]
    transactions_df.to_sql("sales_transactions", conn, if_exists="append", index=False)
    print(f"  -> Inserted {len(transactions_df):,} records into 'sales_transactions' table.")

    # Verification query
    cursor.execute("SELECT COUNT(*) FROM sales_transactions")
    total_tx = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT customer_id) FROM customers")
    total_cust = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT product_id) FROM products")
    total_prod = cursor.fetchone()[0]

    cursor.execute("SELECT ROUND(SUM(sales_revenue), 2), ROUND(SUM(profit), 2) FROM sales_transactions")
    sum_rev, sum_profit = cursor.fetchone()

    conn.commit()
    conn.close()

    print("=" * 60)
    print("DATABASE INITIALIZATION SUCCESSFUL")
    print(f"Database File     : {db_path}")
    print(f"Total Transactions: {total_tx:,}")
    print(f"Total Customers   : {total_cust:,}")
    print(f"Total Products    : {total_prod:,}")
    print(f"Verified Revenue  : ${sum_rev:,.2f}")
    print(f"Verified Profit   : ${sum_profit:,.2f}")
    print("=" * 60)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_file = os.path.join(base_dir, "data", "sales_analytics.db")
    schema_file = os.path.join(base_dir, "sql", "schema.sql")
    clean_csv_file = os.path.join(base_dir, "data", "processed", "sales_data_clean.csv")
    initialize_database(db_file, schema_file, clean_csv_file)
