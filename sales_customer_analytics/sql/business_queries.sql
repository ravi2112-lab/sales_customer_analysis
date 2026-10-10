-- ====================================================================
-- BUSINESS ANALYTICS SQL QUERIES
-- Project: Sales & Customer Data Analytics
-- Target DB: SQLite (sales_analytics.db)
-- Author: Data Analyst Portfolio
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Monthly Revenue & Month-over-Month (MoM) Growth Rate
-- Business Question: How has top-line revenue trended over time, and 
-- what is our month-over-month percentage growth?
-- SQL Techniques: CTEs, Aggregate SUM, Window Function LAG()
-- --------------------------------------------------------------------
-- NAME: monthly_revenue_mom_growth
WITH monthly_sales AS (
    SELECT 
        order_month,
        COUNT(DISTINCT order_id) AS total_orders,
        ROUND(SUM(sales_revenue), 2) AS current_month_revenue,
        ROUND(SUM(profit), 2) AS current_month_profit
    FROM sales_transactions
    GROUP BY order_month
),
monthly_lag AS (
    SELECT 
        order_month,
        total_orders,
        current_month_revenue,
        current_month_profit,
        LAG(current_month_revenue, 1) OVER (ORDER BY order_month) AS previous_month_revenue
    FROM monthly_sales
)
SELECT 
    order_month,
    total_orders,
    current_month_revenue,
    current_month_profit,
    COALESCE(previous_month_revenue, current_month_revenue) AS previous_month_revenue,
    ROUND(
        ((current_month_revenue - COALESCE(previous_month_revenue, current_month_revenue)) 
        / COALESCE(previous_month_revenue, current_month_revenue)) * 100, 
        2
    ) AS mom_growth_pct
FROM monthly_lag
ORDER BY order_month ASC;


-- --------------------------------------------------------------------
-- QUERY 2: Top 3 Most Profitable Products per Category
-- Business Question: In each merchandise category, which 3 products 
-- generate the highest cumulative net profit?
-- SQL Techniques: Multi-table JOIN, CTE, Window Function DENSE_RANK()
-- --------------------------------------------------------------------
-- NAME: top_products_per_category
WITH product_profitability AS (
    SELECT 
        p.category,
        p.sub_category,
        p.product_name,
        COUNT(t.transaction_id) AS units_sold,
        ROUND(SUM(t.sales_revenue), 2) AS total_revenue,
        ROUND(SUM(t.profit), 2) AS total_profit,
        ROUND((SUM(t.profit) / SUM(t.sales_revenue)) * 100, 2) AS margin_pct,
        DENSE_RANK() OVER (
            PARTITION BY p.category 
            ORDER BY SUM(t.profit) DESC
        ) AS profit_rank
    FROM sales_transactions t
    JOIN products p ON t.product_id = p.product_id
    GROUP BY p.category, p.sub_category, p.product_name
)
SELECT 
    category,
    profit_rank,
    product_name,
    sub_category,
    total_revenue,
    total_profit,
    margin_pct
FROM product_profitability
WHERE profit_rank <= 3
ORDER BY category ASC, profit_rank ASC;


-- --------------------------------------------------------------------
-- QUERY 3: Customer RFM (Recency, Frequency, Monetary) Segmentation
-- Business Question: How are our customers distributed across RFM tiers,
-- and who are our top Champion customers?
-- SQL Techniques: CTEs, Window Function NTILE(4), CASE conditional logic
-- --------------------------------------------------------------------
-- NAME: customer_rfm_segmentation
WITH customer_aggregates AS (
    SELECT 
        c.customer_id,
        c.customer_name,
        c.segment,
        c.region,
        CAST(ROUND(JULIANDAY('2025-12-31') - JULIANDAY(MAX(t.order_date))) AS INTEGER) AS recency_days,
        COUNT(DISTINCT t.order_id) AS frequency_orders,
        ROUND(SUM(t.sales_revenue), 2) AS monetary_spend
    FROM customers c
    JOIN sales_transactions t ON c.customer_id = t.customer_id
    GROUP BY c.customer_id, c.customer_name, c.segment, c.region
),
rfm_scores AS (
    SELECT 
        customer_id,
        customer_name,
        segment,
        region,
        recency_days,
        frequency_orders,
        monetary_spend,
        -- Higher score = better (lower recency days is better)
        NTILE(4) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(4) OVER (ORDER BY frequency_orders ASC) AS f_score,
        NTILE(4) OVER (ORDER BY monetary_spend ASC) AS m_score
    FROM customer_aggregates
)
SELECT 
    customer_id,
    customer_name,
    segment,
    region,
    recency_days,
    frequency_orders,
    monetary_spend,
    (r_score + f_score + m_score) AS rfm_total_score,
    CASE 
        WHEN (r_score >= 3 AND f_score >= 3 AND m_score >= 3) THEN 'Champions'
        WHEN (r_score >= 3 AND f_score >= 2) THEN 'Loyal Customers'
        WHEN (r_score >= 3 AND f_score <= 2) THEN 'Recent High-Potentials'
        WHEN (r_score <= 2 AND f_score >= 3) THEN 'At Risk / Need Attention'
        ELSE 'Hibernating / Low Value'
    END AS rfm_segment
FROM rfm_scores
ORDER BY monetary_spend DESC
LIMIT 15;


-- --------------------------------------------------------------------
-- QUERY 4: Discount Impact on Profit Margin
-- Business Question: Does offering higher discounts harm overall profit?
-- What is the margin threshold where discounts become value-destructive?
-- SQL Techniques: CASE categorization, Aggregate AVG/SUM
-- --------------------------------------------------------------------
-- NAME: discount_impact_analysis
SELECT 
    CASE 
        WHEN discount = 0.00 THEN '0% (Full Price)'
        WHEN discount <= 0.05 THEN '1% - 5% Discount'
        WHEN discount <= 0.10 THEN '6% - 10% Discount'
        WHEN discount <= 0.15 THEN '11% - 15% Discount'
        WHEN discount <= 0.20 THEN '16% - 20% Discount'
        WHEN discount <= 0.30 THEN '21% - 30% Discount'
        ELSE 'Over 30% Discount'
    END AS discount_bracket,
    COUNT(*) AS transaction_count,
    ROUND(SUM(sales_revenue), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales_revenue)) * 100, 2) AS realized_margin_pct,
    ROUND(AVG(sales_revenue), 2) AS avg_transaction_value
FROM sales_transactions
GROUP BY discount_bracket
ORDER BY MIN(discount) ASC;


-- --------------------------------------------------------------------
-- QUERY 5: Regional Sales & Profitability Performance
-- Business Question: Which geographic regions drive the highest revenue, 
-- and which generate the healthiest profit margins?
-- SQL Techniques: JOIN, Group By, Regional Aggregations
-- --------------------------------------------------------------------
-- NAME: regional_performance
SELECT 
    c.region,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT t.order_id) AS total_orders,
    SUM(t.quantity) AS units_sold,
    ROUND(SUM(t.sales_revenue), 2) AS total_revenue,
    ROUND(SUM(t.profit), 2) AS total_profit,
    ROUND((SUM(t.profit) / SUM(t.sales_revenue)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(t.sales_revenue) / COUNT(DISTINCT t.order_id), 2) AS aov
FROM sales_transactions t
JOIN customers c ON t.customer_id = c.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 6: Customer Retention & Repeat Purchase Analysis
-- Business Question: How many customers return to make multiple purchases,
-- and what portion of total revenue comes from repeat buyers?
-- SQL Techniques: CTEs, Subqueries, Aggregate Ratios
-- --------------------------------------------------------------------
-- NAME: customer_retention_overview
WITH customer_order_totals AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(sales_revenue) AS total_spend
    FROM sales_transactions
    GROUP BY customer_id
),
retention_summary AS (
    SELECT 
        CASE 
            WHEN total_orders = 1 THEN '1 Order (One-Time Buyer)'
            WHEN total_orders BETWEEN 2 AND 4 THEN '2 - 4 Orders (Repeat Buyer)'
            WHEN total_orders BETWEEN 5 AND 9 THEN '5 - 9 Orders (Frequent Buyer)'
            ELSE '10+ Orders (Power Buyer)'
        END AS loyalty_tier,
        COUNT(customer_id) AS customer_count,
        ROUND(SUM(total_spend), 2) AS tier_revenue
    FROM customer_order_totals
    GROUP BY loyalty_tier
)
SELECT 
    loyalty_tier,
    customer_count,
    ROUND((customer_count * 100.0 / (SELECT COUNT(*) FROM customer_order_totals)), 2) AS pct_of_customers,
    tier_revenue,
    ROUND((tier_revenue * 100.0 / (SELECT SUM(total_spend) FROM customer_order_totals)), 2) AS pct_of_revenue
FROM retention_summary
ORDER BY tier_revenue DESC;


-- --------------------------------------------------------------------
-- QUERY 7: Shipping Mode Efficiency and Lead Time Performance
-- Business Question: What is the average lead time (days to ship) 
-- for each shipping mode, and what is the distribution of orders?
-- SQL Techniques: Date math JULIANDAY(), Filtered aggregation
-- --------------------------------------------------------------------
-- NAME: shipping_lead_times
SELECT 
    ship_mode,
    COUNT(transaction_id) AS total_shipments,
    ROUND(AVG(JULIANDAY(ship_date) - JULIANDAY(order_date)), 2) AS avg_lead_time_days,
    MIN(CAST(JULIANDAY(ship_date) - JULIANDAY(order_date) AS INTEGER)) AS min_lead_time_days,
    MAX(CAST(JULIANDAY(ship_date) - JULIANDAY(order_date) AS INTEGER)) AS max_lead_time_days,
    ROUND(SUM(sales_revenue), 2) AS total_shipped_revenue
FROM sales_transactions
WHERE ship_date IS NOT NULL
GROUP BY ship_mode
ORDER BY avg_lead_time_days ASC;


-- --------------------------------------------------------------------
-- QUERY 8: Return Rate Analysis by Product Sub-Category
-- Business Question: Which merchandise sub-categories suffer the highest
-- return rates, indicating quality or customer expectation issues?
-- SQL Techniques: Conditional Aggregation SUM(CASE WHEN...), Ratio
-- --------------------------------------------------------------------
-- NAME: return_rate_by_subcategory
SELECT 
    p.category,
    p.sub_category,
    COUNT(t.transaction_id) AS total_transactions,
    SUM(CASE WHEN t.order_status = 'Returned' THEN 1 ELSE 0 END) AS returned_transactions,
    ROUND(
        (SUM(CASE WHEN t.order_status = 'Returned' THEN 1.0 ELSE 0.0 END) / COUNT(t.transaction_id)) * 100,
        2
    ) AS return_rate_pct,
    ROUND(SUM(CASE WHEN t.order_status = 'Returned' THEN t.sales_revenue ELSE 0.0 END), 2) AS returned_revenue_loss
FROM sales_transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.category, p.sub_category
ORDER BY return_rate_pct DESC;


-- --------------------------------------------------------------------
-- QUERY 9: Customer Acquisition Cohort Analysis (By Year)
-- Business Question: How has revenue accumulated across customer cohorts 
-- based on the year they made their first purchase?
-- SQL Techniques: Multi-CTE, Subquery JOIN, Cohort Grouping
-- --------------------------------------------------------------------
-- NAME: customer_cohort_analysis
WITH customer_first_order AS (
    SELECT 
        customer_id,
        MIN(order_year) AS cohort_year
    FROM sales_transactions
    GROUP BY customer_id
)
SELECT 
    cfo.cohort_year,
    t.order_year AS purchase_year,
    COUNT(DISTINCT t.customer_id) AS active_customers,
    COUNT(DISTINCT t.order_id) AS total_orders,
    ROUND(SUM(t.sales_revenue), 2) AS cohort_revenue,
    ROUND(SUM(t.profit), 2) AS cohort_profit
FROM sales_transactions t
JOIN customer_first_order cfo ON t.customer_id = cfo.customer_id
GROUP BY cfo.cohort_year, t.order_year
ORDER BY cfo.cohort_year ASC, t.order_year ASC;


-- --------------------------------------------------------------------
-- QUERY 10: Underperforming / Low-Margin Product Audit
-- Business Question: Which products generate the lowest profit margin
-- or drag down overall business profitability?
-- SQL Techniques: JOIN, Group By, Margin Ranking, Bottom Filter
-- --------------------------------------------------------------------
-- NAME: underperforming_products
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.sub_category,
    SUM(t.quantity) AS total_units_sold,
    ROUND(AVG(t.discount) * 100, 2) AS avg_discount_pct,
    ROUND(SUM(t.sales_revenue), 2) AS total_revenue,
    ROUND(SUM(t.profit), 2) AS total_profit,
    ROUND((SUM(t.profit) / SUM(t.sales_revenue)) * 100, 2) AS realized_margin_pct
FROM sales_transactions t
JOIN products p ON t.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category, p.sub_category
ORDER BY realized_margin_pct ASC
LIMIT 10;
