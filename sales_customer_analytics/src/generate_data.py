"""
generate_data.py
----------------
Generates a realistic, multi-year synthetic retail sales & customer dataset
with 7,000+ transaction records for data analytics, SQL queries, and BI reporting.

NOTE ON DATA AUTHENTICITY:
This dataset is 100% SYNTHETIC and generated algorithmically for educational,
portfolio, and demonstration purposes. No real customer or proprietary
corporate data is contained herein.
"""

import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set deterministic random seed for 100% reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

TOTAL_RECORDS = 7200
START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)

# Product catalog hierarchy: Category -> Sub-Category -> [Product Names, Cost Range, Markup Range]
CATALOG = {
    "Technology": {
        "Phones": {
            "products": [
                ("Apple iPhone 15 Pro", 750.0, 999.0),
                ("Samsung Galaxy S24 Ultra", 720.0, 949.0),
                ("Google Pixel 8 Pro", 550.0, 799.0),
                ("OnePlus 12 5G", 480.0, 699.0),
            ],
            "discount_probs": [0.45, 0.25, 0.15, 0.10, 0.05], # 0%, 5%, 10%, 15%, 20%
        },
        "Laptops": {
            "products": [
                ("Apple MacBook Pro 14 M3", 1200.0, 1599.0),
                ("Dell XPS 15 OLED", 1100.0, 1499.0),
                ("Lenovo ThinkPad X1 Carbon", 980.0, 1349.0),
                ("HP Spectre x360", 850.0, 1199.0),
            ],
            "discount_probs": [0.50, 0.20, 0.15, 0.10, 0.05],
        },
        "Accessories": {
            "products": [
                ("Logitech MX Master 3S Mouse", 45.0, 99.0),
                ("Keychron K2 Mechanical Keyboard", 40.0, 89.0),
                ("Anker 737 Power Bank 24K", 60.0, 129.0),
                ("Sony WH-1000XM5 Headphones", 190.0, 349.0),
            ],
            "discount_probs": [0.35, 0.25, 0.20, 0.15, 0.05],
        },
        "Printers": {
            "products": [
                ("HP LaserJet Pro MFP", 180.0, 279.0),
                ("Epson EcoTank ET-4850", 220.0, 399.0),
                ("Brother Monochrome Laser", 120.0, 189.0),
                ("Canon imageCLASS Wireless", 140.0, 229.0),
            ],
            "discount_probs": [0.30, 0.25, 0.20, 0.15, 0.10],
        },
    },
    "Furniture": {
        "Chairs": {
            "products": [
                ("Herman Miller Aeron Ergonomic Chair", 650.0, 1195.0),
                ("Steelcase Gesture Office Chair", 580.0, 1050.0),
                ("Autonomous ErgoChair Pro", 240.0, 449.0),
                ("Mid-Century Mesh Swivel Chair", 110.0, 199.0),
            ],
            "discount_probs": [0.30, 0.25, 0.20, 0.15, 0.10],
        },
        "Bookcases": {
            "products": [
                ("Solid Oak 5-Tier Bookcase", 180.0, 329.0),
                ("Industrial Metal Frame Shelving", 95.0, 179.0),
                ("Minimalist Modular Cube Shelf", 60.0, 119.0),
                ("Corner Floating Wall Bookshelf", 40.0, 79.0),
            ],
            "discount_probs": [0.25, 0.20, 0.25, 0.20, 0.10],
        },
        "Tables": {
            "products": [
                ("Electric Dual-Motor Standing Desk", 280.0, 529.0),
                ("Solid Walnut Conference Table", 650.0, 1199.0),
                ("Compact Foldable Study Desk", 75.0, 139.0),
                ("Executive L-Shaped Corner Desk", 350.0, 649.0),
            ],
            "discount_probs": [0.20, 0.25, 0.25, 0.20, 0.10],
        },
        "Furnishings": {
            "products": [
                ("Architect LED Eye-Care Desk Lamp", 25.0, 59.0),
                ("Anti-Fatigue Ergonomic Floor Mat", 20.0, 49.0),
                ("Acoustic Felt Desk Privacy Screen", 35.0, 79.0),
                ("Adjustable Laptop Riser Stand", 15.0, 39.0),
            ],
            "discount_probs": [0.35, 0.25, 0.20, 0.15, 0.05],
        },
    },
    "Office Supplies": {
        "Storage": {
            "products": [
                ("Steel 3-Drawer Locking File Cabinet", 90.0, 169.0),
                ("Heavy-Duty Clear Plastic Bins (4pk)", 25.0, 54.0),
                ("Desktop Document Organizer Tray", 12.0, 29.0),
                ("Fireproof Document Safe Box", 70.0, 139.0),
            ],
            "discount_probs": [0.35, 0.25, 0.20, 0.15, 0.05],
        },
        "Binders": {
            "products": [
                ("Heavy-Duty D-Ring Binder (3-Pack)", 8.0, 19.99),
                ("Presentation Portfolio Binder", 12.0, 27.99),
                ("Reinforced Spine View Binder", 6.5, 15.49),
                ("Color-Coded Tab Binders Set", 9.0, 22.99),
            ],
            "discount_probs": [0.30, 0.30, 0.20, 0.15, 0.05],
        },
        "Paper": {
            "products": [
                ("Hammermill Premium Multipurpose Paper (Carton)", 22.0, 48.0),
                ("Eco-Friendly Recycled Copy Paper (5 Reams)", 15.0, 34.0),
                ("Heavyweight Glossy Presentation Cardstock", 11.0, 26.0),
                ("Legal Size Continuous Feed Computer Paper", 18.0, 39.0),
            ],
            "discount_probs": [0.35, 0.25, 0.20, 0.15, 0.05],
        },
        "Art": {
            "products": [
                ("Dual-Tip Artist Alcohol Markers (48-Set)", 18.0, 44.99),
                ("Precision Cutting Mat & Craft Blade Set", 10.0, 24.99),
                ("Professional Watercolor Palette & Brushes", 14.0, 32.99),
                ("Self-Healing Rotary Cutting Grid", 8.0, 19.99),
            ],
            "discount_probs": [0.35, 0.25, 0.20, 0.15, 0.05],
        },
    },
}

REGIONS_CITIES = {
    "West": [
        ("California", "Los Angeles"),
        ("California", "San Francisco"),
        ("California", "San Diego"),
        ("Washington", "Seattle"),
        ("Oregon", "Portland"),
        ("Colorado", "Denver"),
    ],
    "East": [
        ("New York", "New York City"),
        ("New York", "Buffalo"),
        ("Massachusetts", "Boston"),
        ("Pennsylvania", "Philadelphia"),
        ("New Jersey", "Newark"),
    ],
    "Central": [
        ("Illinois", "Chicago"),
        ("Texas", "Houston"),
        ("Texas", "Dallas"),
        ("Texas", "Austin"),
        ("Michigan", "Detroit"),
        ("Ohio", "Columbus"),
    ],
    "South": [
        ("Florida", "Miami"),
        ("Florida", "Orlando"),
        ("Georgia", "Atlanta"),
        ("North Carolina", "Charlotte"),
        ("Tennessee", "Nashville"),
        ("Virginia", "Richmond"),
    ],
}

CUSTOMER_NAMES = [
    "Emma Johnson", "Liam Smith", "Olivia Williams", "Noah Brown", "Ava Jones",
    "Oliver Garcia", "Sophia Miller", "Elijah Davis", "Isabella Rodriguez", "Lucas Martinez",
    "Mia Hernandez", "Mason Lopez", "Harper Gonzalez", "Ethan Wilson", "Evelyn Anderson",
    "James Thomas", "Abigail Taylor", "Aiden Moore", "Emily Jackson", "Alexander Martin",
    "Ella Lee", "Henry Perez", "Elizabeth Thompson", "Sebastian White", "Camila Harris",
    "Jack Sanchez", "Luna Clark", "Owen Ramirez", "Aria Lewis", "Daniel Robinson",
    "Chloe Walker", "Matthew Young", "Penelope Allen", "Jackson King", "Layla Wright",
    "David Scott", "Grace Torres", "Carter Nguyen", "Zoey Hill", "Wyatt Flores",
    "Nora Green", "Jayden Adams", "Riley Nelson", "John Baker", "Zoey Hall",
    "Luke Rivera", "Hannah Campbell", "Asher Mitchell", "Lillian Carter", "Gabriel Roberts",
    "Addison Gomez", "Anthony Phillips", "Eleanor Evans", "Dylan Turner", "Natalie Diaz",
    "Leo Parker", "Aubrey Cruz", "Isaac Edwards", "Victoria Collins", "Julian Reyes"
]

SEGMENTS = ["Consumer", "Corporate", "Home Office"]
SEGMENT_WEIGHTS = [0.52, 0.30, 0.18]

SHIP_MODES = ["Standard Class", "Second Class", "First Class", "Same Day"]
SHIP_WEIGHTS = [0.60, 0.20, 0.14, 0.06]

PAYMENT_METHODS = ["Credit Card", "PayPal", "Bank Transfer", "Debit Card"]
PAYMENT_WEIGHTS = [0.48, 0.28, 0.14, 0.10]

DISCOUNT_VALUES = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40]


def generate_synthetic_dataset(output_path: str):
    """Generates synthetic sales records with realistic distributions."""
    print("Generating synthetic sales dataset...")
    
    # Generate a pool of 1,200 unique customers
    customer_pool = []
    for i in range(1, 1201):
        cid = f"CUST-{i:04d}"
        cname = f"{random.choice(CUSTOMER_NAMES)} {random.choice(['Jr.', 'Sr.', 'II', 'III', ''])}".strip()
        cseg = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
        region = random.choice(list(REGIONS_CITIES.keys()))
        state, city = random.choice(REGIONS_CITIES[region])
        customer_pool.append({
            "customer_id": cid,
            "customer_name": cname,
            "segment": cseg,
            "region": region,
            "state": state,
            "city": city
        })

    # Total days span
    total_days = (END_DATE - START_DATE).days
    records = []

    for idx in range(1, TOTAL_RECORDS + 1):
        # Pick random day with seasonality (Q4 spike for holiday sales)
        day_offset = random.randint(0, total_days)
        order_date = START_DATE + timedelta(days=day_offset)
        month = order_date.month
        
        # Seasonality boost: Nov & Dec have 50% higher probability
        if month in [11, 12] and random.random() < 0.25:
            day_offset = random.randint(0, total_days)
            order_date = START_DATE + timedelta(days=day_offset)

        # Pick customer (using power law / Pareto distribution so repeat customers occur)
        cust_idx = int(np.random.pareto(a=1.5) * 120) % len(customer_pool)
        cust = customer_pool[cust_idx]

        # Pick category & product
        cat_name = random.choice(list(CATALOG.keys()))
        sub_name = random.choice(list(CATALOG[cat_name].keys()))
        sub_info = CATALOG[cat_name][sub_name]
        prod_tuple = random.choice(sub_info["products"])
        prod_name, unit_cost, unit_price = prod_tuple

        # Quantity
        if cust["segment"] == "Corporate":
            quantity = random.choices([1, 2, 3, 4, 5, 8, 10], weights=[0.20, 0.25, 0.20, 0.15, 0.10, 0.06, 0.04])[0]
        else:
            quantity = random.choices([1, 2, 3, 4, 5], weights=[0.45, 0.30, 0.15, 0.07, 0.03])[0]

        # Discount: higher discounts occasionally to simulate margin squeeze
        discount = random.choices(
            [0.0, 0.05, 0.10, 0.15, 0.20, 0.30, 0.40],
            weights=[0.40, 0.22, 0.18, 0.10, 0.05, 0.03, 0.02]
        )[0]

        # Shipping mode and lead time
        ship_mode = random.choices(SHIP_MODES, weights=SHIP_WEIGHTS)[0]
        lead_days_map = {
            "Same Day": 0,
            "First Class": random.choice([1, 2]),
            "Second Class": random.choice([2, 3, 4]),
            "Standard Class": random.choice([4, 5, 6, 7])
        }
        lead_days = lead_days_map[ship_mode]
        ship_date = order_date + timedelta(days=lead_days)

        # Order Status
        status_choice = random.choices(
            ["Delivered", "Shipped", "Processing", "Returned"],
            weights=[0.88, 0.05, 0.03, 0.04]
        )[0]

        # Raw financial calculations
        gross_sales = round(unit_price * quantity, 2)
        sales_revenue = round(gross_sales * (1.0 - discount), 2)
        cogs = round(unit_cost * quantity, 2)
        profit = round(sales_revenue - cogs, 2)
        profit_margin = round((profit / sales_revenue), 4) if sales_revenue > 0 else 0.0

        payment_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]

        # Order ID: group some items under the same order
        order_num = 10000 + (idx // 2) if idx % 3 == 0 else 10000 + idx
        order_id = f"ORD-{order_date.year}-{order_num:05d}"
        product_id = f"PROD-{cat_name[:3].upper()}-{abs(hash(prod_name)) % 10000:04d}"

        # Inject realistic raw anomalies for data cleaning demonstrations:
        # 1. Trailing whitespaces in some text fields
        # 2. Occasional casing inconsistencies
        # 3. Missing ship_date for 'Processing' orders
        cat_for_row = cat_name
        city_for_row = cust["city"]
        ship_date_str = ship_date.strftime("%Y-%m-%d")

        if idx % 95 == 0:
            cat_for_row = cat_name.lower() # Inconsistent lowercase
        if idx % 80 == 0:
            city_for_row = f"  {cust['city']}  " # Whitespace padding
        if status_choice == "Processing":
            ship_date_str = None # Unshipped orders have null ship_date

        records.append({
            "order_id": order_id,
            "order_date": order_date.strftime("%Y-%m-%d"),
            "ship_date": ship_date_str,
            "ship_mode": ship_mode,
            "customer_id": cust["customer_id"],
            "customer_name": cust["customer_name"],
            "segment": cust["segment"],
            "country": "United States",
            "region": cust["region"],
            "state": cust["state"],
            "city": city_for_row,
            "product_id": product_id,
            "category": cat_for_row,
            "sub_category": sub_name,
            "product_name": prod_name,
            "unit_cost": unit_cost,
            "unit_price": unit_price,
            "quantity": quantity,
            "discount": discount,
            "sales_revenue": sales_revenue,
            "cogs": cogs,
            "profit": profit,
            "profit_margin": profit_margin,
            "order_status": status_choice,
            "payment_method": payment_method,
            "data_source": "SYNTHETIC_DATASET"
        })

    # Add 25 intentional duplicate records for cleaning detection
    duplicate_samples = random.sample(records, 25)
    records.extend(duplicate_samples)

    df = pd.DataFrame(records)
    
    # Ensure destination folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df):,} synthetic rows saved to: {output_path}")
    print(f"Unique Customers: {df['customer_id'].nunique():,}")
    print(f"Unique Orders: {df['order_id'].nunique():,}")
    print(f"Date Range: {df['order_date'].min()} to {df['order_date'].max()}")
    return df


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_csv = os.path.join(base_dir, "data", "raw", "sales_data_raw.csv")
    generate_synthetic_dataset(target_csv)
