"""
Task 11 — Two visualizations

Creates:
1. visualizations/return_rate_by_payment.png
2. visualizations/monthly_revenue_trend.png

The calculations are reproduced from the same raw CSVs and cleaning
rules used in clean_and_eda.py, so the script is fully re-runnable.
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# ============================================================
# SETUP
# ============================================================

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "visualizations"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOAD RAW DATA
# ============================================================

orders = pd.read_csv(DATA_DIR / "orders.csv")
customers = pd.read_csv(DATA_DIR / "customers.csv")
products = pd.read_csv(DATA_DIR / "products.csv")


# ============================================================
# SAME CLEANING LOGIC AS TASKS 2–6
# ============================================================

# Task 2 — Standardize payment method
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)


# Task 3 — Remove duplicate natural-key orders
KEY = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned",
]

dup_mask = orders.duplicated(
    subset=KEY,
    keep="first"
)

orders_clean = orders.loc[~dup_mask].copy()


# Task 4 — Impute missing values
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"]
    .fillna(0)
)

median_rating = orders_clean["rating"].median()

orders_clean["rating"] = (
    orders_clean["rating"]
    .fillna(median_rating)
)


# Task 5 — Merge products and customers
merged = (
    orders_clean
    .merge(products, on="product_id", how="left")
    .merge(customers, on="customer_id", how="left")
)

# Calculate order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)


# Task 6 — IQR outlier detection
q1 = merged["quantity"].quantile(0.25)
q3 = merged["quantity"].quantile(0.75)

iqr = q3 - q1

lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)


# ============================================================
# TASK 11.1
# RETURN RATE BY PAYMENT METHOD
# ============================================================

payment_rates = (
    merged
    .groupby("payment_method")["returned"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

fig, ax = plt.subplots(figsize=(8, 5))

bars = ax.bar(
    payment_rates.index,
    payment_rates.values
)

# Exact percentage on each bar
for bar, rate in zip(bars, payment_rates.values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height(),
        f"{rate:.1f}%",
        ha="center",
        va="bottom"
    )

cod_rate = payment_rates["COD"]
card_rate = payment_rates["CARD"]

cod_multiple = cod_rate / card_rate

ax.set_title(
    f"COD Returns at {cod_rate:.1f}% — {cod_multiple:.0f}x Card"
)

ax.set_xlabel("Payment Method")
ax.set_ylabel("Return Rate (%)")

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "return_rate_by_payment.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# TASK 11.2
# OUTLIER-CORRECTED MONTHLY REVENUE
# ============================================================

merged["month"] = (
    pd.to_datetime(merged["order_date"])
    .dt.to_period("M")
    .astype(str)
)

# IMPORTANT:
# Exclude the quantity outliers identified in Task 6.
# This is the corrected revenue required by Task 11.
monthly_revenue = (
    merged.loc[~merged["is_outlier"]]
    .groupby("month")["order_value"]
    .sum()
    .sort_index()
)

peak_month = monthly_revenue.idxmax()
peak_revenue = monthly_revenue.max()


fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o"
)

ax.set_title(
    f"Outlier-Corrected Monthly Revenue — Peak: {peak_month}"
)

ax.set_xlabel("Month")
ax.set_ylabel("Revenue (Rs)")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "monthly_revenue_trend.png",
    dpi=150,
    bbox_inches="tight"
)

plt.close()


# ============================================================
# FINAL CHECK
# ============================================================

print("=" * 60)
print("TASK 11 COMPLETE")
print("=" * 60)

print(
    "Created:",
    OUTPUT_DIR / "return_rate_by_payment.png"
)

print(
    "Created:",
    OUTPUT_DIR / "monthly_revenue_trend.png"
)

print(
    f"Peak month: {peak_month}"
)

print(
    f"Peak corrected revenue: Rs {peak_revenue:,.2f}"
)

print("\nPayment return rates:")
print(payment_rates.round(1).to_string())
