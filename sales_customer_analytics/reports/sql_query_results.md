# SQL Business Analytics Query Results

> **Project**: Sales & Customer Data Analytics
> **Database Engine**: SQLite 3 (`data/sales_analytics.db`)
> **Generated Automatically**: Yes

---

## Query 1: `monthly_revenue_mom_growth`

```sql
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
```

**Results (15 of 36 rows shown):**

| order_month   |   total_orders |   current_month_revenue |   current_month_profit |   previous_month_revenue |   mom_growth_pct |
|:--------------|---------------:|------------------------:|-----------------------:|-------------------------:|-----------------:|
| 2023-01       |            207 |                  185120 |                62321.7 |                   185120 |             0    |
| 2023-02       |            201 |                  145098 |                45439.6 |                   185120 |           -21.62 |
| 2023-03       |            228 |                  164252 |                54774.2 |                   145098 |            13.2  |
| 2023-04       |            194 |                  160327 |                49547.4 |                   164252 |            -2.39 |
| 2023-05       |            226 |                  186886 |                63139.4 |                   160327 |            16.57 |
| 2023-06       |            212 |                  155268 |                47349.6 |                   186886 |           -16.92 |
| 2023-07       |            216 |                  132997 |                44559.6 |                   155268 |           -14.34 |
| 2023-08       |            189 |                  119690 |                36897.9 |                   132997 |           -10.01 |
| 2023-09       |            197 |                  168215 |                52882.7 |                   119690 |            40.54 |
| 2023-10       |            225 |                  176210 |                55500.8 |                   168215 |             4.75 |
| 2023-11       |            144 |                  120754 |                36563.9 |                   176210 |           -31.47 |
| 2023-12       |            156 |                  119412 |                40758.4 |                   120754 |            -1.11 |
| 2024-01       |            189 |                  171761 |                55931.6 |                   119412 |            43.84 |
| 2024-02       |            205 |                  122909 |                42651.4 |                   171761 |           -28.44 |
| 2024-03       |            202 |                  217978 |                65761.2 |                   122909 |            77.35 |

---

## Query 2: `top_products_per_category`

```sql
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
```

**Results (9 of 9 rows shown):**

| category        |   profit_rank | product_name                             | sub_category   |   total_revenue |   total_profit |   margin_pct |
|:----------------|--------------:|:-----------------------------------------|:---------------|----------------:|---------------:|-------------:|
| Furniture       |             1 | Herman Miller Aeron Ergonomic Chair      | Chairs         |        373736   |      154036    |        41.22 |
| Furniture       |             2 | Steelcase Gesture Office Chair           | Chairs         |        357788   |      143188    |        40.02 |
| Furniture       |             3 | Solid Walnut Conference Table            | Tables         |        287820   |      118170    |        41.06 |
| Office Supplies |             1 | Steel 3-Drawer Locking File Cabinet      | Storage        |         48181.9 |       20731.9  |        43.03 |
| Office Supplies |             2 | Fireproof Document Safe Box              | Storage        |         43805.8 |       19935.8  |        45.51 |
| Office Supplies |             3 | Dual-Tip Artist Alcohol Markers (48-Set) | Art            |         14914.1 |        8614.09 |        57.76 |
| Technology      |             1 | Apple MacBook Pro 14 M3                  | Laptops        |        552614   |      109814    |        19.87 |
| Technology      |             2 | Dell XPS 15 OLED                         | Laptops        |        461542   |       98542.1  |        21.35 |
| Technology      |             3 | Lenovo ThinkPad X1 Carbon                | Laptops        |        393571   |       81930.8  |        20.82 |

---

## Query 3: `customer_rfm_segmentation`

```sql
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
```

**Results (15 of 15 rows shown):**

| customer_id   | customer_name        | segment     | region   |   recency_days |   frequency_orders |   monetary_spend |   rfm_total_score | rfm_segment   |
|:--------------|:---------------------|:------------|:---------|---------------:|-------------------:|-----------------:|------------------:|:--------------|
| CUST-0006     | Lillian Carter Sr.   | Corporate   | Central  |              4 |                 95 |         111092   |                12 | Champions     |
| CUST-0009     | Abigail Taylor Jr.   | Corporate   | West     |             51 |                 67 |         102135   |                12 | Champions     |
| CUST-0002     | Evelyn Anderson Sr.  | Corporate   | West     |              2 |                 83 |          85155.6 |                12 | Champions     |
| CUST-0026     | Hannah Campbell Jr.  | Corporate   | Central  |             16 |                 56 |          85087.9 |                12 | Champions     |
| CUST-0005     | Luna Clark Sr.       | Consumer    | Central  |              4 |                100 |          69872.1 |                12 | Champions     |
| CUST-0001     | Nora Green Jr.       | Consumer    | Central  |             12 |                 84 |          63771.7 |                12 | Champions     |
| CUST-0015     | Nora Green Sr.       | Corporate   | East     |              1 |                 70 |          61973.3 |                12 | Champions     |
| CUST-0040     | David Scott Sr.      | Corporate   | West     |             37 |                 45 |          60719.1 |                12 | Champions     |
| CUST-0029     | Victoria Collins Jr. | Home Office | Central  |             48 |                 58 |          59472.7 |                12 | Champions     |
| CUST-0008     | Oliver Garcia III    | Consumer    | Central  |             44 |                 90 |          58727.1 |                12 | Champions     |
| CUST-0014     | Riley Nelson II      | Corporate   | West     |             12 |                 63 |          56903.4 |                12 | Champions     |
| CUST-0044     | Addison Gomez III    | Corporate   | East     |             18 |                 42 |          54625.2 |                12 | Champions     |
| CUST-0030     | Penelope Allen       | Consumer    | Central  |             27 |                 51 |          53419   |                12 | Champions     |
| CUST-0037     | Lillian Carter Sr.   | Corporate   | South    |             22 |                 36 |          53078.6 |                12 | Champions     |
| CUST-0034     | Hannah Campbell III  | Corporate   | East     |              9 |                 45 |          52026.2 |                12 | Champions     |

---

## Query 4: `discount_impact_analysis`

```sql
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
```

**Results (7 of 7 rows shown):**

| discount_bracket   |   transaction_count |    total_revenue |   total_profit |   realized_margin_pct |   avg_transaction_value |
|:-------------------|--------------------:|-----------------:|---------------:|----------------------:|------------------------:|
| 0% (Full Price)    |                2873 |      2.3275e+06  |      852975    |                 36.65 |                  810.13 |
| 1% - 5% Discount   |                1625 |      1.22691e+06 |      414308    |                 33.77 |                  755.02 |
| 6% - 10% Discount  |                1278 |      1.00306e+06 |      302180    |                 30.13 |                  784.86 |
| 11% - 15% Discount |                 689 | 528098           |      127858    |                 24.21 |                  766.47 |
| 16% - 20% Discount |                 373 | 278424           |       59346.7  |                 21.32 |                  746.45 |
| 21% - 30% Discount |                 220 |  99878.1         |       11704.1  |                 11.72 |                  453.99 |
| Over 30% Discount  |                 142 |  88340.9         |       -6025.58 |                 -6.82 |                  622.12 |

---

## Query 5: `regional_performance`

```sql
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
```

**Results (4 of 4 rows shown):**

| region   |   total_customers |   total_orders |   units_sold |   total_revenue |   total_profit |   profit_margin_pct |    aov |
|:---------|------------------:|---------------:|-------------:|----------------:|---------------:|--------------------:|-------:|
| Central  |               205 |           2081 |         4711 |     1.63233e+06 |         521744 |               31.96 | 784.4  |
| West     |               215 |           1687 |         4051 |     1.4265e+06  |         456015 |               31.97 | 845.58 |
| East     |               211 |           1870 |         4360 |     1.40126e+06 |         439846 |               31.39 | 749.33 |
| South    |               191 |           1457 |         3213 |     1.09212e+06 |         344741 |               31.57 | 749.57 |

---

## Query 6: `customer_retention_overview`

```sql
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
```

**Results (4 of 4 rows shown):**

| loyalty_tier                  |   customer_count |   pct_of_customers |     tier_revenue |   pct_of_revenue |
|:------------------------------|-----------------:|-------------------:|-----------------:|-----------------:|
| 10+ Orders (Power Buyer)      |              176 |              21.41 |      4.18034e+06 |            75.29 |
| 5 - 9 Orders (Frequent Buyer) |              111 |              13.5  | 598920           |            10.79 |
| 2 - 4 Orders (Repeat Buyer)   |              261 |              31.75 | 571876           |            10.3  |
| 1 Order (One-Time Buyer)      |              274 |              33.33 | 201070           |             3.62 |

---

## Query 7: `shipping_lead_times`

```sql
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
```

**Results (4 of 4 rows shown):**

| ship_mode      |   total_shipments |   avg_lead_time_days |   min_lead_time_days |   max_lead_time_days |   total_shipped_revenue |
|:---------------|------------------:|---------------------:|---------------------:|---------------------:|------------------------:|
| Same Day       |               438 |                 0    |                    0 |                    0 |        372938           |
| First Class    |               952 |                 1.48 |                    1 |                    2 |        676718           |
| Second Class   |              1426 |                 3.01 |                    2 |                    4 |             1.08545e+06 |
| Standard Class |              4152 |                 5.47 |                    4 |                    7 |             3.24795e+06 |

---

## Query 8: `return_rate_by_subcategory`

```sql
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
```

**Results (12 of 12 rows shown):**

| category        | sub_category   |   total_transactions |   returned_transactions |   return_rate_pct |   returned_revenue_loss |
|:----------------|:---------------|---------------------:|------------------------:|------------------:|------------------------:|
| Technology      | Laptops        |                  595 |                      29 |              4.87 |                86619.6  |
| Office Supplies | Storage        |                  564 |                      27 |              4.79 |                 5025.1  |
| Technology      | Accessories    |                  636 |                      28 |              4.4  |                 9632.6  |
| Furniture       | Furnishings    |                  650 |                      28 |              4.31 |                 3315.05 |
| Furniture       | Bookcases      |                  592 |                      24 |              4.05 |                 5357.4  |
| Office Supplies | Binders        |                  606 |                      24 |              3.96 |                  978.74 |
| Office Supplies | Art            |                  614 |                      23 |              3.75 |                 1574.32 |
| Furniture       | Tables         |                  585 |                      21 |              3.59 |                19544.2  |
| Furniture       | Chairs         |                  606 |                      20 |              3.3  |                24554.8  |
| Technology      | Phones         |                  579 |                      18 |              3.11 |                34294.1  |
| Office Supplies | Paper          |                  573 |                      15 |              2.62 |                 1035.6  |
| Technology      | Printers       |                  600 |                      13 |              2.17 |                 6043.15 |

---

## Query 9: `customer_cohort_analysis`

```sql
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
```

**Results (6 of 6 rows shown):**

|   cohort_year |   purchase_year |   active_customers |   total_orders |   cohort_revenue |   cohort_profit |
|--------------:|----------------:|-------------------:|---------------:|-----------------:|----------------:|
|          2023 |            2023 |                533 |           2282 |      1.83423e+06 |        589735   |
|          2023 |            2024 |                360 |           1997 |      1.73665e+06 |        546657   |
|          2023 |            2025 |                370 |           2095 |      1.55512e+06 |        501827   |
|          2024 |            2024 |                174 |            235 | 217831           |         65869.9 |
|          2024 |            2025 |                 70 |            113 | 101229           |         27384.7 |
|          2025 |            2025 |                115 |            139 | 107145           |         30872.9 |

---

## Query 10: `underperforming_products`

```sql
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
```

**Results (10 of 10 rows shown):**

| product_id    | product_name              | category   | sub_category   |   total_units_sold |   avg_discount_pct |   total_revenue |   total_profit |   realized_margin_pct |
|:--------------|:--------------------------|:-----------|:---------------|-------------------:|-------------------:|----------------:|---------------:|----------------------:|
| PROD-TEC-5308 | Samsung Galaxy S24 Ultra  | Technology | Phones         |                274 |               7.04 |        241900   |        44620.1 |                 18.45 |
| PROD-TEC-3866 | Apple iPhone 15 Pro       | Technology | Phones         |                341 |               7.27 |        313986   |        58235.7 |                 18.55 |
| PROD-TEC-3415 | Apple MacBook Pro 14 M3   | Technology | Laptops        |                369 |               6.32 |        552614   |       109814   |                 19.87 |
| PROD-TEC-9014 | Lenovo ThinkPad X1 Carbon | Technology | Laptops        |                318 |               9.27 |        393571   |        81930.8 |                 20.82 |
| PROD-TEC-6450 | Dell XPS 15 OLED          | Technology | Laptops        |                330 |               6.73 |        461542   |        98542.1 |                 21.35 |
| PROD-TEC-1035 | HP Spectre x360           | Technology | Laptops        |                313 |               7.93 |        342255   |        76204.6 |                 22.27 |
| PROD-TEC-2622 | Google Pixel 8 Pro        | Technology | Phones         |                353 |               8.16 |        261193   |        67043.1 |                 25.67 |
| PROD-TEC-3867 | OnePlus 12 5G             | Technology | Phones         |                317 |               7.36 |        204947   |        52786.8 |                 25.76 |
| PROD-TEC-4942 | HP LaserJet Pro MFP       | Technology | Printers       |                330 |               7.74 |         84732.3 |        25332.3 |                 29.9  |
| PROD-TEC-6399 | Brother Monochrome Laser  | Technology | Printers       |                267 |               6.64 |         47353.9 |        15314   |                 32.34 |

---
