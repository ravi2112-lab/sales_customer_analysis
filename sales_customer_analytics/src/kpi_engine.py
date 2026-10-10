"""
kpi_engine.py
-------------
Computes core business and operational Key Performance Indicators (KPIs)
from the cleaned sales transactions dataset.

KPIs calculated:
1. Total Revenue ($)
2. Total Profit ($)
3. Total Orders (Distinct)
4. Total Customers (Distinct)
5. Average Order Value (AOV) ($)
6. Overall Profit Margin (%)
7. Total Quantity Sold (Units)
8. Return Rate (%)
9. Repeat Customer Rate (%)
10. Multi-dimensional breakdowns: By Segment, By Category, By Region, By Year/Quarter
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any


def compute_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Computes headline KPIs from a sales DataFrame."""
    total_revenue = float(df["sales_revenue"].sum())
    total_cogs = float(df["cogs"].sum())
    total_profit = float(df["profit"].sum())
    total_orders = int(df["order_id"].nunique())
    total_customers = int(df["customer_id"].nunique())
    total_quantity = int(df["quantity"].sum())

    aov = total_revenue / total_orders if total_orders > 0 else 0.0
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0.0
    avg_units_per_order = total_quantity / total_orders if total_orders > 0 else 0.0

    # Return rate
    returned_orders = df[df["order_status"] == "Returned"]["order_id"].nunique()
    return_rate = (returned_orders / total_orders * 100) if total_orders > 0 else 0.0

    # Repeat customer rate
    customer_order_counts = df.groupby("customer_id")["order_id"].nunique()
    repeat_customers = (customer_order_counts > 1).sum()
    repeat_rate = (repeat_customers / total_customers * 100) if total_customers > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_cogs": round(total_cogs, 2),
        "total_profit": round(total_profit, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_quantity": total_quantity,
        "aov": round(aov, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "avg_units_per_order": round(avg_units_per_order, 2),
        "return_rate_pct": round(return_rate, 2),
        "repeat_customer_rate_pct": round(repeat_rate, 2),
    }


def compute_segment_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Breakdown of metrics by Customer Segment."""
    seg = df.groupby("segment").agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        units_sold=("quantity", "sum"),
    ).reset_index()
    seg["aov"] = (seg["revenue"] / seg["orders"]).round(2)
    seg["profit_margin_pct"] = ((seg["profit"] / seg["revenue"]) * 100).round(2)
    seg["revenue_share_pct"] = ((seg["revenue"] / seg["revenue"].sum()) * 100).round(2)
    return seg.sort_values(by="revenue", ascending=False)


def compute_category_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Breakdown of metrics by Product Category & Sub-category."""
    cat = df.groupby(["category", "sub_category"]).agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        avg_discount=("discount", "mean")
    ).reset_index()
    cat["profit_margin_pct"] = ((cat["profit"] / cat["revenue"]) * 100).round(2)
    cat["avg_discount_pct"] = (cat["avg_discount"] * 100).round(2)
    cat["revenue"] = cat["revenue"].round(2)
    cat["profit"] = cat["profit"].round(2)
    return cat.sort_values(by="revenue", ascending=False)


def compute_regional_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Breakdown of metrics by Geographic Region."""
    reg = df.groupby("region").agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        units_sold=("quantity", "sum"),
    ).reset_index()
    reg["profit_margin_pct"] = ((reg["profit"] / reg["revenue"]) * 100).round(2)
    reg["aov"] = (reg["revenue"] / reg["orders"]).round(2)
    reg["revenue"] = reg["revenue"].round(2)
    reg["profit"] = reg["profit"].round(2)
    return reg.sort_values(by="revenue", ascending=False)


def compute_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Year-over-Year comparison of performance."""
    yearly = df.groupby("order_year").agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        units_sold=("quantity", "sum"),
    ).reset_index()
    yearly["profit_margin_pct"] = ((yearly["profit"] / yearly["revenue"]) * 100).round(2)
    yearly["aov"] = (yearly["revenue"] / yearly["orders"]).round(2)
    yearly["revenue_growth_yoy_pct"] = yearly["revenue"].pct_change().fillna(0).mul(100).round(2)
    yearly["profit_growth_yoy_pct"] = yearly["profit"].pct_change().fillna(0).mul(100).round(2)
    yearly["revenue"] = yearly["revenue"].round(2)
    yearly["profit"] = yearly["profit"].round(2)
    return yearly


def print_kpi_summary(df: pd.DataFrame) -> None:
    """Prints a beautiful, formatted executive KPI scorecard to stdout."""
    kpis = compute_kpis(df)
    print("\n" + "=" * 65)
    print("           EXECUTIVE KPI SCORECARD (SALES & CUSTOMERS)          ")
    print("=" * 65)
    print(f"  • Total Revenue        : ${kpis['total_revenue']:>14,.2f}")
    print(f"  • Total Net Profit     : ${kpis['total_profit']:>14,.2f}")
    print(f"  • Overall Profit Margin: {kpis['profit_margin_pct']:>13.2f}%")
    print(f"  • Total Orders Placed  : {kpis['total_orders']:>14,d}")
    print(f"  • Total Unique Customers: {kpis['total_customers']:>13,d}")
    print(f"  • Average Order Value  : ${kpis['aov']:>14,.2f}")
    print(f"  • Total Quantity Sold  : {kpis['total_quantity']:>14,d} units")
    print(f"  • Avg Units Per Order  : {kpis['avg_units_per_order']:>14.2f}")
    print(f"  • Repeat Customer Rate : {kpis['repeat_customer_rate_pct']:>13.2f}%")
    print(f"  • Overall Return Rate  : {kpis['return_rate_pct']:>13.2f}%")
    print("=" * 65 + "\n")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_csv = os.path.join(base_dir, "data", "processed", "sales_data_clean.csv")
    if os.path.exists(clean_csv):
        df_clean = pd.read_csv(clean_csv)
        print_kpi_summary(df_clean)
        print("Segment Breakdown:")
        print(compute_segment_kpis(df_clean).to_string(index=False))
    else:
        print(f"Processed file not found at {clean_csv}. Run data_cleaning.py first.")
