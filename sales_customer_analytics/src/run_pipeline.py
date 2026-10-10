"""
run_pipeline.py
---------------
Master end-to-end data pipeline runner for Sales & Customer Data Analytics.

Orchestrates the entire sequence:
1. Synthetic Data Generation (7,000+ realistic transactions)
2. Data Cleaning & Validation Pipeline
3. Relational SQLite Database Initialization & Star-Schema Ingestion
4. Business Analytics SQL Queries Execution & Report Generation
5. Publication-Ready EDA Visualizations Generation
6. Executive KPI Summary Scorecard Calculation
"""

import os
import sys
import time

# Ensure src and root directories are on python search path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, CURRENT_DIR)

from src.generate_data import generate_synthetic_dataset
from src.data_cleaning import clean_sales_data
from src.kpi_engine import print_kpi_summary, compute_segment_kpis
from src.eda_analysis import run_eda
from sql.init_db import initialize_database
from sql.run_sql_queries import run_queries_and_report
import pandas as pd


def run_full_pipeline():
    start_time = time.time()
    print("\n" + "=" * 70)
    print("      SALES & CUSTOMER DATA ANALYTICS: MASTER PIPELINE EXECUTION      ")
    print("=" * 70)

    # Relative paths
    raw_csv = os.path.join(PROJECT_ROOT, "data", "raw", "sales_data_raw.csv")
    clean_csv = os.path.join(PROJECT_ROOT, "data", "processed", "sales_data_clean.csv")
    db_file = os.path.join(PROJECT_ROOT, "data", "sales_analytics.db")
    schema_file = os.path.join(PROJECT_ROOT, "sql", "schema.sql")
    sql_queries_file = os.path.join(PROJECT_ROOT, "sql", "business_queries.sql")
    sql_report_file = os.path.join(PROJECT_ROOT, "reports", "sql_query_results.md")
    screenshots_dir = os.path.join(PROJECT_ROOT, "screenshots")

    # Step 1: Generate Synthetic Data
    print("\n[STEP 1/6] Generating synthetic retail sales dataset...")
    generate_synthetic_dataset(raw_csv)

    # Step 2: Clean and Preprocess Data
    print("\n[STEP 2/6] Cleaning, auditing, and preprocessing dataset...")
    df_clean = clean_sales_data(raw_csv, clean_csv)

    # Step 3: Initialize SQLite Database & Ingest Clean Data
    print("\n[STEP 3/6] Setting up SQLite analytics database & loading tables...")
    initialize_database(db_file, schema_file, clean_csv)

    # Step 4: Execute SQL Business Queries
    print("\n[STEP 4/6] Running 10 business SQL analytics queries...")
    run_queries_and_report(db_file, sql_queries_file, sql_report_file)

    # Step 5: Generate Exploratory Visualizations
    print("\n[STEP 5/6] Generating 6 publication-ready EDA charts...")
    run_eda(clean_csv, screenshots_dir)

    # Step 6: Compute & Display Executive KPIs
    print("\n[STEP 6/6] Computing final executive KPI scorecard...")
    print_kpi_summary(df_clean)

    elapsed = time.time() - start_time
    print("=" * 70)
    print(f" PIPELINE COMPLETE IN {elapsed:.2f} SECONDS")
    print(f" Clean Data CSV      : {clean_csv}")
    print(f" SQLite Database     : {db_file}")
    print(f" SQL Query Report    : {sql_report_file}")
    print(f" Visual Charts Saved : {screenshots_dir}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_full_pipeline()
