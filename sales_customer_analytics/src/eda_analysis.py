"""
eda_analysis.py
---------------
Performs exploratory data analysis (EDA) using Pandas, NumPy, Matplotlib, and Seaborn.
Generates 6 publication-quality analytical visualization figures saved to 'screenshots/'
for inclusion in portfolio documentation, README, and reports.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import pandas as pd
import numpy as np

# Set global aesthetics for clean, modern portfolio charts
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11
plt.rcParams["axes.labelweight"] = "semibold"
plt.rcParams["figure.dpi"] = 300

PRIMARY_COLOR = "#1f77b4"
SECONDARY_COLOR = "#2ca02c"
ACCENT_COLOR = "#d62728"
PALETTE = ["#2b5c8f", "#3c8dbc", "#56b4e9", "#009e73", "#f0e442", "#d55e00", "#cc79a7"]


def plot_monthly_trend(df: pd.DataFrame, output_dir: str):
    """Plot 1: Monthly Revenue & Profit Trend with 3-Month Rolling Average."""
    monthly = df.groupby("order_month").agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    monthly["rolling_rev"] = monthly["revenue"].rolling(3, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Revenue Bars
    bars = ax1.bar(
        range(len(monthly)),
        monthly["revenue"] / 1000,
        color="#34495e",
        alpha=0.4,
        label="Monthly Revenue ($K)",
        width=0.6
    )

    # Rolling Trend Line
    ax1.plot(
        range(len(monthly)),
        monthly["rolling_rev"] / 1000,
        color="#2980b9",
        linewidth=2.5,
        marker="o",
        label="3-Month Moving Avg Revenue ($K)"
    )

    # Net Profit Line
    ax1.plot(
        range(len(monthly)),
        monthly["profit"] / 1000,
        color="#27ae60",
        linewidth=2.2,
        linestyle="--",
        marker="s",
        label="Net Profit ($K)"
    )

    ax1.set_title("Monthly Revenue & Profit Growth Trend (2023 - 2025)", pad=15)
    ax1.set_xlabel("Order Month (YYYY-MM)")
    ax1.set_ylabel("Financial Amount ($ in Thousands)")
    ax1.set_xticks(range(0, len(monthly), 2))
    ax1.set_xticklabels(monthly["order_month"].iloc[::2], rotation=45, ha="right")
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax1.legend(loc="upper left", frameon=True)
    ax1.grid(axis="y", linestyle=":", alpha=0.7)

    plt.tight_layout()
    out_file = os.path.join(output_dir, "01_monthly_revenue_profit_trend.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def plot_category_performance(df: pd.DataFrame, output_dir: str):
    """Plot 2: Product Sub-Category Performance (Revenue vs Profit Margin)."""
    sub_perf = df.groupby(["category", "sub_category"]).agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum")
    ).reset_index()
    sub_perf["margin_pct"] = (sub_perf["profit"] / sub_perf["revenue"]) * 100
    sub_perf = sub_perf.sort_values(by="revenue", ascending=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7), sharey=True)

    # Left: Total Revenue
    palette_cat = {"Technology": "#2b5c8f", "Furniture": "#e67e22", "Office Supplies": "#27ae60"}
    bar_colors = [palette_cat.get(c, "#7f8c8d") for c in sub_perf["category"]]

    y_pos = range(len(sub_perf))
    ax1.barh(y_pos, sub_perf["revenue"] / 1000, color=bar_colors, alpha=0.85)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(sub_perf["sub_category"])
    ax1.set_xlabel("Total Sales Revenue ($K)")
    ax1.set_title("Total Sales Revenue by Sub-Category")
    ax1.xaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax1.grid(axis="x", linestyle=":", alpha=0.7)

    # Right: Profit Margin %
    margin_colors = ["#27ae60" if m >= 25 else "#e74c3c" for m in sub_perf["margin_pct"]]
    ax2.barh(y_pos, sub_perf["margin_pct"], color=margin_colors, alpha=0.85)
    ax2.set_xlabel("Realized Profit Margin (%)")
    ax2.set_title("Realized Net Profit Margin (%)")
    ax2.axvline(x=sub_perf["margin_pct"].mean(), color="black", linestyle="--", linewidth=1.5,
                label=f"Avg Margin ({sub_perf['margin_pct'].mean():.1f}%)")
    ax2.legend(loc="lower right")
    ax2.grid(axis="x", linestyle=":", alpha=0.7)

    plt.suptitle("Product Sub-Category Financial Matrix: Sales Revenue vs Realized Profit Margin", fontsize=14, y=1.02)
    plt.tight_layout()
    out_file = os.path.join(output_dir, "02_category_subcategory_performance.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def plot_regional_matrix(df: pd.DataFrame, output_dir: str):
    """Plot 3: Regional Sales & Profit Comparison."""
    regional = df.groupby("region").agg(
        revenue=("sales_revenue", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique")
    ).reset_index().sort_values(by="revenue", ascending=False)
    regional["margin_pct"] = (regional["profit"] / regional["revenue"]) * 100

    x = np.arange(len(regional))
    width = 0.35

    fig, ax1 = plt.subplots(figsize=(10, 6))

    rects1 = ax1.bar(x - width/2, regional["revenue"] / 1000, width, label="Revenue ($K)", color="#2980b9")
    rects2 = ax1.bar(x + width/2, regional["profit"] / 1000, width, label="Net Profit ($K)", color="#27ae60")

    ax1.set_title("Geographic Performance: Sales Revenue & Net Profit by Region", pad=15)
    ax1.set_xlabel("Geographic Region")
    ax1.set_ylabel("Financial Volume ($ in Thousands)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(regional["region"])
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter("${x:,.0f}K"))
    ax1.legend(loc="upper right")
    ax1.grid(axis="y", linestyle=":", alpha=0.7)

    # Add margin annotation on top of profit bars
    for idx, row in regional.iterrows():
        margin = row["margin_pct"]
        ax1.annotate(
            f"Margin:\n{margin:.1f}%",
            xy=(x[idx] + width/2, (row["profit"] / 1000) + 15),
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#145a32"
        )

    plt.tight_layout()
    out_file = os.path.join(output_dir, "03_regional_sales_profit_matrix.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def plot_discount_sensitivity(df: pd.DataFrame, output_dir: str):
    """Plot 4: Discount Impact on Realized Profit Margin."""
    fig, ax = plt.subplots(figsize=(11, 6))

    discount_summary = df.groupby("discount").agg(
        avg_margin=("profit_margin", "mean"),
        median_margin=("profit_margin", "median"),
        total_rev=("sales_revenue", "sum"),
        count=("order_id", "count")
    ).reset_index()

    sns.boxplot(
        x="discount",
        y="profit_margin",
        hue="discount",
        data=df,
        palette="Blues_r",
        legend=False,
        showmeans=True,
        meanprops={"marker": "o", "markerfacecolor": "red", "markeredgecolor": "black", "markersize": "7"},
        ax=ax
    )

    ax.axhline(0, color="#c0392b", linestyle="--", linewidth=1.5, label="Break-Even Threshold (0% Profit)")
    ax.set_title("Impact of Discounting on Realized Profit Margin Distribution", pad=15)
    ax.set_xlabel("Discount Rate Applied")
    ax.set_ylabel("Profit Margin Ratio")
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(xmax=1.0))
    discount_ticks = sorted(df["discount"].unique())
    ax.set_xticks(range(len(discount_ticks)))
    ax.set_xticklabels([f"{int(d*100)}%" for d in discount_ticks])
    ax.legend(loc="lower left")

    plt.tight_layout()
    out_file = os.path.join(output_dir, "04_discount_vs_profit_margin.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def plot_rfm_segments(df: pd.DataFrame, output_dir: str):
    """Plot 5: Customer RFM Segmentation Distribution."""
    # Compute RFM
    snapshot_date = pd.to_datetime(df["order_date"]).max()
    cust_rfm = df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (snapshot_date - pd.to_datetime(x).max()).days),
        frequency=("order_id", "nunique"),
        monetary=("sales_revenue", "sum")
    ).reset_index()

    # Simple 4-tier quantile segmentation
    cust_rfm["r_score"] = pd.qcut(cust_rfm["recency"].rank(method="first"), 4, labels=[4, 3, 2, 1])
    cust_rfm["f_score"] = pd.qcut(cust_rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4])
    cust_rfm["m_score"] = pd.qcut(cust_rfm["monetary"].rank(method="first"), 4, labels=[1, 2, 3, 4])

    def assign_segment(row):
        score = int(row["r_score"]) + int(row["f_score"]) + int(row["m_score"])
        if score >= 10:
            return "Champions"
        elif score >= 8:
            return "Loyal Customers"
        elif score >= 6:
            return "Potential Loyalists"
        elif score >= 4:
            return "At Risk"
        else:
            return "Hibernating"

    cust_rfm["segment"] = cust_rfm.apply(assign_segment, axis=1)
    seg_summary = cust_rfm.groupby("segment").agg(
        customers=("customer_id", "count"),
        total_spend=("monetary", "sum")
    ).reset_index().sort_values(by="total_spend", ascending=False)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = ["#2ecc71", "#3498db", "#f39c12", "#e67e22", "#e74c3c"]

    # Customer Counts Bar Chart
    ax1.bar(range(len(seg_summary)), seg_summary["customers"], color=colors, alpha=0.85)
    ax1.set_title("Customer Count by RFM Segment")
    ax1.set_ylabel("Number of Customers")
    ax1.set_xticks(range(len(seg_summary)))
    ax1.set_xticklabels(seg_summary["segment"], rotation=30, ha="right")
    ax1.grid(axis="y", linestyle=":", alpha=0.7)

    # Revenue Contribution Doughnut Chart
    ax2.pie(
        seg_summary["total_spend"],
        labels=seg_summary["segment"],
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )
    ax2.set_title("Revenue Contribution by RFM Segment")

    plt.suptitle("Customer Value Segmentation (RFM Analysis)", fontsize=14, y=1.02)
    plt.tight_layout()
    out_file = os.path.join(output_dir, "05_customer_rfm_segments.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def plot_shipping_modes(df: pd.DataFrame, output_dir: str):
    """Plot 6: Shipping Mode Lead Time Performance."""
    df_shipped = df[df["ship_date"].notnull()].copy()
    lead_time = (pd.to_datetime(df_shipped["ship_date"]) - pd.to_datetime(df_shipped["order_date"])).dt.days
    df_shipped["lead_time_days"] = lead_time

    fig, ax = plt.subplots(figsize=(10, 5.5))

    order_modes = ["Same Day", "First Class", "Second Class", "Standard Class"]
    sns.barplot(
        x="ship_mode",
        y="lead_time_days",
        hue="ship_mode",
        data=df_shipped,
        order=order_modes,
        palette="crest",
        legend=False,
        errorbar=None,
        ax=ax
    )

    ax.set_title("Fulfillment Efficiency: Average Delivery Lead Time by Shipping Tier", pad=15)
    ax.set_xlabel("Shipping Mode")
    ax.set_ylabel("Average Lead Time (Days)")
    ax.grid(axis="y", linestyle=":", alpha=0.7)

    # Add numeric labels on bars
    lead_avgs = df_shipped.groupby("ship_mode")["lead_time_days"].mean().to_dict()
    for idx, mode in enumerate(order_modes):
        avg_val = lead_avgs.get(mode, 0.0)
        ax.text(idx, avg_val + 0.1, f"{avg_val:.2f} Days", ha="center", fontweight="bold", fontsize=10)

    plt.tight_layout()
    out_file = os.path.join(output_dir, "06_shipping_mode_lead_time_distribution.png")
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()
    print(f"Saved: {out_file}")


def run_eda(clean_csv_path: str, screenshots_dir: str):
    """Main EDA coordinator generating all charts and descriptive summary."""
    print("=" * 60)
    print("RUNNING EXPLORATORY DATA ANALYSIS (EDA)")
    print("=" * 60)

    if not os.path.exists(clean_csv_path):
        raise FileNotFoundError(f"Clean CSV not found at: {clean_csv_path}")

    os.makedirs(screenshots_dir, exist_ok=True)
    df = pd.read_csv(clean_csv_path)

    print(f"Loaded {len(df):,} cleaned records for exploratory plotting.")
    print("Generating charts...")

    plot_monthly_trend(df, screenshots_dir)
    plot_category_performance(df, screenshots_dir)
    plot_regional_matrix(df, screenshots_dir)
    plot_discount_sensitivity(df, screenshots_dir)
    plot_rfm_segments(df, screenshots_dir)
    plot_shipping_modes(df, screenshots_dir)

    print("=" * 60)
    print("ALL 6 EDA VISUALIZATIONS GENERATED & SAVED")
    print(f"Destination: {screenshots_dir}")
    print("=" * 60)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    clean_csv = os.path.join(base_dir, "data", "processed", "sales_data_clean.csv")
    shots_dir = os.path.join(base_dir, "screenshots")
    run_eda(clean_csv, shots_dir)
