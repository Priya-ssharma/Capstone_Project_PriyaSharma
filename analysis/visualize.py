import os
import pandas as pd
import matplotlib.pyplot as plt

# Task 11 - Create visualizations

os.makedirs("visualizations", exist_ok=True)

# Load raw data
customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")

# Clean payment method
orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

# Remove duplicate orders
natural_key = [
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "discount_pct",
    "payment_method",
    "rating",
    "returned"
]

duplicate_mask = orders.duplicated(
    subset=natural_key,
    keep="first"
)

orders_clean = orders[~duplicate_mask].copy()

# Impute missing values
orders_clean["discount_pct"] = (
    orders_clean["discount_pct"].fillna(0)
)

rating_median = orders_clean["rating"].median()

orders_clean["rating"] = (
    orders_clean["rating"].fillna(rating_median)
)

# Merge orders with products
merged = orders_clean.merge(
    products,
    on="product_id",
    how="left"
)

# Merge with customers
merged = merged.merge(
    customers,
    on="customer_id",
    how="left"
)

# Calculate order value
merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

# Task 11A - Return rate by payment method
return_rate = (
    orders_clean
    .groupby("payment_method")["returned"]
    .mean()
    .mul(100)
)

print("Return rate by payment method:")
print(return_rate.round(1))

plt.figure(figsize=(8, 5))

return_rate.plot(kind="bar")

plt.title("Return Rate by Payment Method")
plt.xlabel("Payment Method")
plt.ylabel("Return Rate (%)")
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig(
    "visualizations/return_rate_by_payment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

# Task 11B - Monthly revenue trend
merged["order_date"] = pd.to_datetime(
    merged["order_date"]
)

merged["year_month"] = (
    merged["order_date"]
    .dt.to_period("M")
    .astype(str)
)

# Identify quantity outliers using IQR
Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)
IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

merged["is_outlier"] = (
    (merged["quantity"] < lower)
    | (merged["quantity"] > upper)
)

# Exclude outliers for corrected monthly revenue
merged_without_outliers = merged[
    ~merged["is_outlier"]
].copy()

monthly_revenue = (
    merged_without_outliers
    .groupby("year_month")["order_value"]
    .sum()
)

print("\nCorrected monthly revenue:")
print(monthly_revenue.round(2))

peak_month = monthly_revenue.idxmax()
peak_value = monthly_revenue.max()

print(
    f"\nActual peak month: {peak_month} "
    f"with revenue ₹{peak_value:,.2f}"
)

plt.figure(figsize=(10, 5))

plt.plot(
    monthly_revenue.index,
    monthly_revenue.values,
    marker="o"
)

plt.title("Monthly Revenue Trend (Outlier-Corrected)")
plt.xlabel("Month")
plt.ylabel("Revenue (₹)")
plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "visualizations/monthly_revenue_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print("\nTASK 11 VISUALIZATIONS COMPLETED")
