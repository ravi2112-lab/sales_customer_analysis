-- ====================================================================
-- SCHEMA DEFINITION: Sales & Customer Analytics Database
-- Database: SQLite (sales_analytics.db)
-- Description: Star-schema inspired relational model for analytics
-- ====================================================================

-- Drop existing tables if re-initializing
DROP TABLE IF EXISTS sales_transactions;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;

-- 1. Customers Dimension Table
CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    segment VARCHAR(50) NOT NULL,
    country VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL
);

-- 2. Products Dimension Table
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(50) NOT NULL,
    sub_category VARCHAR(50) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL
);

-- 3. Sales Transactions Fact Table
CREATE TABLE sales_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id VARCHAR(30) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE,
    ship_mode VARCHAR(50) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount DECIMAL(4, 2) NOT NULL CHECK (discount >= 0.0 AND discount <= 1.0),
    sales_revenue DECIMAL(12, 2) NOT NULL,
    cogs DECIMAL(12, 2) NOT NULL,
    profit DECIMAL(12, 2) NOT NULL,
    profit_margin DECIMAL(6, 4) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    order_year INTEGER NOT NULL,
    order_quarter VARCHAR(5) NOT NULL,
    order_month VARCHAR(7) NOT NULL,
    order_day_of_week VARCHAR(15) NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Optimization Indexes for Analytics & Query Performance
CREATE INDEX idx_sales_order_date ON sales_transactions(order_date);
CREATE INDEX idx_sales_customer_id ON sales_transactions(customer_id);
CREATE INDEX idx_sales_product_id ON sales_transactions(product_id);
CREATE INDEX idx_sales_order_month ON sales_transactions(order_month);
CREATE INDEX idx_sales_status ON sales_transactions(order_status);
