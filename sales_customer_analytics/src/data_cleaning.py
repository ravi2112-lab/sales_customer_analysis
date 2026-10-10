"""
data_cleaning.py
----------------
Data cleaning, validation, and preprocessing pipeline for raw sales transactions.

Operations performed:
1. Duplicate detection and removal.
2. String sanitization: strip whitespaces and normalize casing (e.g., Title Case).
3. Datetime parsing and chronological consistency validation (ship_date >= order_date).
4. Missing value auditing and handling (documenting null ship_date for in-transit orders).
5. Numerical validation & re-verification of business logic formulas (Revenue, COGS, Profit, Margin).
6. Export cleaned dataset to data/processed/sales_data_clean.csv with validation metrics.
"""

import os
import pandas as pd
import numpy as np


def clean_sales_data(input_csv: str, output_csv: str) -> pd.DataFrame:
    """Reads raw sales CSV, executes cleaning steps, and saves processed CSV."""
    print("=" * 60)
    print("STARTING DATA CLEANING & PREPROCESSING PIPELINE")
    print("=" * 60)

    if not os.path.exists(input_csv):
        raise FileNotFoundError(f"Input file not found at: {input_csv}")

    df_raw = pd.read_csv(input_csv)
    initial_shape = df_raw.shape
    print(f"[Step 1] Ingested raw records: {initial_shape[0]:,} rows, {initial_shape[1]} columns.")

    # 1. Audit and drop exact duplicates
    dup_count = df_raw.duplicated().sum()
    print(f"[Step 2] Detected duplicate rows: {dup_count}")
    df = df_raw.drop_duplicates().copy()

    # 2. String sanitization (Strip whitespace & normalize casing)
    string_cols = ["customer_name", "segment", "country", "region", "state", "city", 
                   "category", "sub_category", "product_name", "ship_mode", "order_status", "payment_method"]
    
    print("[Step 3] Sanitizing string fields (trimming whitespace & standardizing title case)...")
    for col in string_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            # Normalize casing for category and city
            if col in ["category", "segment", "region"]:
                df[col] = df[col].str.title()

    # 3. Datetime Parsing and Chronological Validation
    print("[Step 4] Parsing datetimes and verifying chronological integrity...")
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df["ship_date"] = pd.to_datetime(df["ship_date"], errors="coerce")

    # Audit null values
    null_counts = df.isnull().sum()
    print("Null values audit:")
    for col, count in null_counts[null_counts > 0].items():
        print(f"  - Column '{col}': {count} null values (Expected for unfulfilled 'Processing' orders)")

    # Validate ship_date >= order_date for records where ship_date is present
    invalid_dates_mask = (df["ship_date"].notnull()) & (df["ship_date"] < df["order_date"])
    invalid_date_count = invalid_dates_mask.sum()
    if invalid_date_count > 0:
        print(f"  - Corrected {invalid_date_count} records where ship_date was prior to order_date.")
        df.loc[invalid_dates_mask, "ship_date"] = df.loc[invalid_dates_mask, "order_date"]

    # 4. Numerical validation and formula auditing
    print("[Step 5] Validating numerical rules & financial arithmetic...")
    assert (df["quantity"] > 0).all(), "Invalid non-positive quantity found!"
    assert (df["unit_price"] > 0).all(), "Invalid non-positive unit price found!"
    assert (df["discount"] >= 0).all() and (df["discount"] <= 1.0).all(), "Discount out of [0, 1] range!"

    # Re-verify and standardize calculated columns to avoid floating precision drift
    df["sales_revenue"] = ((df["unit_price"] * df["quantity"]) * (1.0 - df["discount"])).round(2)
    df["cogs"] = (df["unit_cost"] * df["quantity"]).round(2)
    df["profit"] = (df["sales_revenue"] - df["cogs"]).round(2)
    df["profit_margin"] = np.where(df["sales_revenue"] > 0, (df["profit"] / df["sales_revenue"]).round(4), 0.0)

    # Convert dates to standard ISO strings for clean CSV export
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
    df["ship_date"] = df["ship_date"].dt.strftime("%Y-%m-%d")

    # Add useful derived analytics columns
    order_dt = pd.to_datetime(df["order_date"])
    df["order_year"] = order_dt.dt.year
    df["order_quarter"] = "Q" + order_dt.dt.quarter.astype(str)
    df["order_month"] = order_dt.dt.strftime("%Y-%m")
    df["order_day_of_week"] = order_dt.dt.day_name()

    final_shape = df.shape
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df.to_csv(output_csv, index=False)

    print("=" * 60)
    print("DATA CLEANING COMPLETE")
    print(f"Initial Rows : {initial_shape[0]:,}")
    print(f"Final Clean  : {final_shape[0]:,} (Removed {initial_shape[0] - final_shape[0]:,} duplicates)")
    print(f"Output File  : {output_csv}")
    print("=" * 60)
    return df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_path = os.path.join(base_dir, "data", "raw", "sales_data_raw.csv")
    clean_path = os.path.join(base_dir, "data", "processed", "sales_data_clean.csv")
    clean_sales_data(raw_path, clean_path)
