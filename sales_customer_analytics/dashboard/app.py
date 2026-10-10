"""
app.py
------
Interactive Executive Web Dashboard for Sales & Customer Data Analytics.
Built with Streamlit, Pandas, Altair, and SQLite.

Features:
- Global Dynamic Sidebar Filters (Date Range, Region, Category, Segment)
- Executive KPI Metric Cards with dynamic calculations
- Interactive Visualizations (Trends, Category Margins, Regional Matrix, RFM Segments)
- Live SQL Query Studio (Run pre-configured business queries or custom SQL)
- Raw Data Explorer with instant CSV export
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import streamlit as st

# Configure Streamlit page layout
st.set_page_config(
    page_title="Sales & Customer Data Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Relative directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_CLEAN_PATH = os.path.join(BASE_DIR, "data", "processed", "sales_data_clean.csv")
DB_PATH = os.path.join(BASE_DIR, "data", "sales_analytics.db")
SQL_QUERIES_PATH = os.path.join(BASE_DIR, "sql", "business_queries.sql")


@st.cache_data
def load_data():
    """Loads and caches the cleaned transaction dataset."""
    if not os.path.exists(DATA_CLEAN_PATH):
        st.error(f"Processed dataset not found at {DATA_CLEAN_PATH}. Please run src/run_pipeline.py first.")
        st.stop()
    df = pd.read_csv(DATA_CLEAN_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["ship_date"] = pd.to_datetime(df["ship_date"])
    return df


@st.cache_data
def load_sql_queries():
    """Reads named queries from sql/business_queries.sql."""
    if not os.path.exists(SQL_QUERIES_PATH):
        return {}
    import re
    with open(SQL_QUERIES_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    pattern = r"-- NAME:\s*([a-zA-Z0-9_]+)\s*\n(.*?)(?=(?:-- NAME:|$))"
    matches = re.findall(pattern, content, re.DOTALL)
    queries = {}
    for name, sql in matches:
        cleaned = re.sub(r"--.*$", "", sql, flags=re.MULTILINE).strip().rstrip(";")
        queries[name] = cleaned
    return queries


# -------------------------------------------------------------
# Custom CSS for Modern Executive Aesthetics
# -------------------------------------------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .kpi-value {
        font-size: 1.7rem;
        font-weight: 700;
        color: #0f172a;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 500;
    }
    .badge-synthetic {
        display: inline-block;
        background-color: #fef3c7;
        color: #92400e;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-left: 10px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# Data Loading & Sidebar Navigation
# -------------------------------------------------------------
df_raw = load_data()

st.sidebar.markdown("## ⚙️ Filter Controls")
st.sidebar.markdown("Slice and dice sales transactions across dimensions:")

# Date filter
min_date = df_raw["order_date"].min().date()
max_date = df_raw["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Region filter
all_regions = sorted(df_raw["region"].unique().tolist())
selected_regions = st.sidebar.multiselect("Geographic Regions", all_regions, default=all_regions)

# Category filter
all_categories = sorted(df_raw["category"].unique().tolist())
selected_categories = st.sidebar.multiselect("Product Categories", all_categories, default=all_categories)

# Segment filter
all_segments = sorted(df_raw["segment"].unique().tolist())
selected_segments = st.sidebar.multiselect("Customer Segments", all_segments, default=all_segments)

# Apply filters
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_d, end_d = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start_d, end_d = pd.to_datetime(min_date), pd.to_datetime(max_date)

filtered_df = df_raw[
    (df_raw["order_date"] >= start_d) &
    (df_raw["order_date"] <= end_d) &
    (df_raw["region"].isin(selected_regions)) &
    (df_raw["category"].isin(selected_categories)) &
    (df_raw["segment"].isin(selected_segments))
]

st.sidebar.markdown("---")
st.sidebar.info(f"Showing **{len(filtered_df):,}** of **{len(df_raw):,}** transactions ({len(filtered_df)/len(df_raw)*100:.1f}%)")

# -------------------------------------------------------------
# Main Header
# -------------------------------------------------------------
st.markdown('<div class="main-header">Sales & Customer Data Analytics Dashboard <span class="badge-synthetic">SYNTHETIC BENCHMARK DATASET</span></div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Executive performance cockpit, KPI tracking, cohort RFM analysis, and relational SQL studio.</div>', unsafe_allow_html=True)

# -------------------------------------------------------------
# Headline KPI Scorecards
# -------------------------------------------------------------
rev = filtered_df["sales_revenue"].sum()
prof = filtered_df["profit"].sum()
margin = (prof / rev * 100) if rev > 0 else 0.0
orders_count = filtered_df["order_id"].nunique()
customers_count = filtered_df["customer_id"].nunique()
aov = (rev / orders_count) if orders_count > 0 else 0.0
qty_sold = filtered_df["quantity"].sum()

# Repeat customer rate
cust_order_counts = filtered_df.groupby("customer_id")["order_id"].nunique()
repeat_cust_pct = (cust_order_counts > 1).sum() / customers_count * 100 if customers_count > 0 else 0.0

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Revenue</div>
        <div class="kpi-value">${rev:,.0f}</div>
        <div class="kpi-sub">Across {orders_count:,} orders</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Net Profit</div>
        <div class="kpi-value">${prof:,.0f}</div>
        <div class="kpi-sub">{margin:.2f}% Profit Margin</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Average Order Value</div>
        <div class="kpi-value">${aov:,.2f}</div>
        <div class="kpi-sub">{qty_sold/orders_count:.1f} units / order</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Orders</div>
        <div class="kpi-value">{orders_count:,}</div>
        <div class="kpi-sub">{qty_sold:,} units sold</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Unique Customers</div>
        <div class="kpi-value">{customers_count:,}</div>
        <div class="kpi-sub">{repeat_cust_pct:.1f}% Repeat Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col6:
    return_rate = (filtered_df[filtered_df["order_status"] == "Returned"]["order_id"].nunique() / orders_count * 100) if orders_count > 0 else 0.0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Return Rate</div>
        <div class="kpi-value">{return_rate:.2f}%</div>
        <div class="kpi-sub">Delivered: {(filtered_df['order_status']=='Delivered').mean()*100:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------
# Multi-Tab Analytical Views
# -------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Executive Overview",
    "📦 Product & Category Analytics",
    "👥 Customer & RFM Segmentation",
    "💻 SQL Query Explorer",
    "📋 Data Explorer & Export"
])

# -------------------------------------------------------------
# TAB 1: EXECUTIVE OVERVIEW
# -------------------------------------------------------------
with tab1:
    st.subheader("Monthly Revenue & Net Profit Trend")
    
    # Monthly aggregation
    monthly_df = filtered_df.groupby("order_month").agg(
        Revenue=("sales_revenue", "sum"),
        Profit=("profit", "sum")
    ).reset_index()
    monthly_df["Moving_Avg_Revenue"] = monthly_df["Revenue"].rolling(3, min_periods=1).mean()

    col_chart, col_side = st.columns([2.5, 1])

    with col_chart:
        st.line_chart(
            monthly_df.set_index("order_month")[["Revenue", "Profit", "Moving_Avg_Revenue"]],
            use_container_width=True,
            height=340
        )
        st.caption("Blue: Total Revenue | Red: Net Profit | Green: 3-Month Rolling Average Revenue")

    with col_side:
        st.markdown("#### Regional Contribution")
        reg_df = filtered_df.groupby("region").agg(
            Revenue=("sales_revenue", "sum"),
            Profit=("profit", "sum")
        ).reset_index()
        reg_df["Margin"] = (reg_df["Profit"] / reg_df["Revenue"] * 100).round(1)
        st.dataframe(
            reg_df.style.format({"Revenue": "${:,.0f}", "Profit": "${:,.0f}", "Margin": "{:.1f}%"}),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Sales by Customer Segment")
        seg_summary = filtered_df.groupby("segment").agg(
            Revenue=("sales_revenue", "sum"),
            Orders=("order_id", "nunique"),
            AOV=("sales_revenue", lambda x: x.sum() / filtered_df.loc[x.index, "order_id"].nunique())
        ).reset_index()
        st.bar_chart(seg_summary.set_index("segment")["Revenue"], use_container_width=True)

    with c2:
        st.subheader("Sales by Product Category")
        cat_summary = filtered_df.groupby("category").agg(
            Revenue=("sales_revenue", "sum"),
            Profit=("profit", "sum")
        ).reset_index()
        st.bar_chart(cat_summary.set_index("category")[["Revenue", "Profit"]], use_container_width=True)


# -------------------------------------------------------------
# TAB 2: PRODUCT & CATEGORY ANALYTICS
# -------------------------------------------------------------
with tab2:
    st.subheader("Product Sub-Category Financial Matrix")
    sub_perf = filtered_df.groupby(["category", "sub_category"]).agg(
        Revenue=("sales_revenue", "sum"),
        Profit=("profit", "sum"),
        Units_Sold=("quantity", "sum"),
        Avg_Discount=("discount", lambda x: x.mean() * 100)
    ).reset_index()
    sub_perf["Profit_Margin_%"] = (sub_perf["Profit"] / sub_perf["Revenue"] * 100).round(2)
    sub_perf = sub_perf.sort_values(by="Revenue", ascending=False)

    st.dataframe(
        sub_perf.style.format({
            "Revenue": "${:,.2f}",
            "Profit": "${:,.2f}",
            "Units_Sold": "{:,}",
            "Avg_Discount": "{:.1f}%",
            "Profit_Margin_%": "{:.2f}%"
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    p1, p2 = st.columns(2)
    with p1:
        st.subheader("Top 5 Products by Net Profit")
        top_prods = filtered_df.groupby("product_name").agg(
            Profit=("profit", "sum"),
            Revenue=("sales_revenue", "sum")
        ).reset_index().sort_values(by="Profit", ascending=False).head(5)
        st.dataframe(
            top_prods.style.format({"Profit": "${:,.2f}", "Revenue": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )

    with p2:
        st.subheader("Discount Sensitivity: Margin Erosion")
        disc_summary = filtered_df.groupby("discount").agg(
            Revenue=("sales_revenue", "sum"),
            Profit=("profit", "sum"),
            Orders=("order_id", "count")
        ).reset_index()
        disc_summary["Margin_%"] = (disc_summary["Profit"] / disc_summary["Revenue"] * 100).round(2)
        disc_summary["Discount_Rate"] = (disc_summary["discount"] * 100).astype(int).astype(str) + "%"
        st.bar_chart(disc_summary.set_index("Discount_Rate")["Margin_%"], use_container_width=True)
        st.caption("Notice how realized profit margins drop sharply as discount rate exceeds 15%.")


# -------------------------------------------------------------
# TAB 3: CUSTOMER & RFM SEGMENTATION
# -------------------------------------------------------------
with tab3:
    st.subheader("Customer Value & RFM Segmentation")
    st.markdown("Customers are scored across **Recency** (days since last purchase), **Frequency** (order volume), and **Monetary Value** (total revenue spend).")

    snapshot_date = filtered_df["order_date"].max()
    cust_rfm = filtered_df.groupby(["customer_id", "customer_name", "segment", "region"]).agg(
        Recency_Days=("order_date", lambda x: (snapshot_date - x.max()).days),
        Order_Count=("order_id", "nunique"),
        Total_Spend=("sales_revenue", "sum")
    ).reset_index()

    if len(cust_rfm) >= 4:
        cust_rfm["R_Score"] = pd.qcut(cust_rfm["Recency_Days"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
        cust_rfm["F_Score"] = pd.qcut(cust_rfm["Order_Count"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        cust_rfm["M_Score"] = pd.qcut(cust_rfm["Total_Spend"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
        
        def assign_tier(row):
            total = row["R_Score"] + row["F_Score"] + row["M_Score"]
            if total >= 10:
                return "Champions"
            elif total >= 8:
                return "Loyal Customers"
            elif total >= 6:
                return "Potential Loyalists"
            elif total >= 4:
                return "At Risk"
            else:
                return "Hibernating"

        cust_rfm["RFM_Segment"] = cust_rfm.apply(assign_tier, axis=1)

        rfm_agg = cust_rfm.groupby("RFM_Segment").agg(
            Customer_Count=("customer_id", "count"),
            Total_Revenue=("Total_Spend", "sum"),
            Avg_Orders=("Order_Count", "mean"),
            Avg_Spend=("Total_Spend", "mean")
        ).reset_index().sort_values(by="Total_Revenue", ascending=False)

        col_rfm1, col_rfm2 = st.columns([1, 1])
        with col_rfm1:
            st.markdown("#### Segment Distribution")
            st.dataframe(
                rfm_agg.style.format({
                    "Customer_Count": "{:,}",
                    "Total_Revenue": "${:,.0f}",
                    "Avg_Orders": "{:.1f}",
                    "Avg_Spend": "${:,.0f}"
                }),
                use_container_width=True,
                hide_index=True
            )
        with col_rfm2:
            st.markdown("#### Revenue by Segment")
            st.bar_chart(rfm_agg.set_index("RFM_Segment")["Total_Revenue"], use_container_width=True)

        st.markdown("---")
        st.markdown("#### Top 10 High-Value Customers (Champions)")
        top_custs = cust_rfm.sort_values(by="Total_Spend", ascending=False).head(10)[[
            "customer_id", "customer_name", "segment", "region", "Order_Count", "Total_Spend", "Recency_Days", "RFM_Segment"
        ]]
        st.dataframe(
            top_custs.style.format({"Total_Spend": "${:,.2f}"}),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("Not enough customer records under the active filter selection to perform RFM quantile ranking.")


# -------------------------------------------------------------
# TAB 4: SQL QUERY EXPLORER
# -------------------------------------------------------------
with tab4:
    st.subheader("Relational SQL Business Query Studio")
    st.markdown("Execute pre-compiled production business queries or write and test custom SQL queries directly against the SQLite database.")

    queries = load_sql_queries()
    query_names = list(queries.keys())

    selected_query_name = st.selectbox(
        "Choose a Business SQL Query template:",
        options=query_names,
        index=0 if query_names else None
    )

    default_sql = queries.get(selected_query_name, "SELECT * FROM sales_transactions LIMIT 10;")
    custom_sql = st.text_area("SQL Statement (Editable):", value=default_sql, height=180)

    col_btn, col_info = st.columns([1, 4])
    with col_btn:
        run_query = st.button("▶ Run SQL Query", type="primary")

    if run_query or custom_sql:
        try:
            conn = sqlite3.connect(DB_PATH)
            sql_res_df = pd.read_sql_query(custom_sql, conn)
            conn.close()

            st.success(f"Query returned **{len(sql_res_df):,}** rows.")
            st.dataframe(sql_res_df, use_container_width=True)

            csv_res = sql_res_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download SQL Results as CSV",
                data=csv_res,
                file_name=f"sql_query_result_{selected_query_name}.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"SQL Execution Error: {e}")


# -------------------------------------------------------------
# TAB 5: DATA EXPLORER & EXPORT
# -------------------------------------------------------------
with tab5:
    st.subheader("Filtered Transactions Dataset Explorer")
    st.markdown("Inspect granular records matching active sidebar filters, sort by columns, and export to CSV.")

    search_term = st.text_input("🔍 Search by Customer Name, Order ID, or Product Name:", "")
    view_df = filtered_df.copy()
    if search_term:
        mask = (
            view_df["customer_name"].str.contains(search_term, case=False, na=False) |
            view_df["order_id"].str.contains(search_term, case=False, na=False) |
            view_df["product_name"].str.contains(search_term, case=False, na=False)
        )
        view_df = view_df[mask]

    st.dataframe(
        view_df[[
            "order_id", "order_date", "customer_name", "segment", "region", "category",
            "sub_category", "product_name", "quantity", "discount", "sales_revenue",
            "profit", "profit_margin", "order_status"
        ]].head(500),
        use_container_width=True
    )
    st.caption(f"Displaying {min(len(view_df), 500):,} of {len(view_df):,} matching rows.")

    csv_data = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_data,
        file_name="sales_customer_filtered_data.csv",
        mime="text/csv",
        type="primary"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem;">
    <strong>Sales & Customer Data Analytics Project</strong> • Designed for Data Analyst Portfolios • Python, Pandas, SQLite, Streamlit
</div>
""", unsafe_allow_html=True)
