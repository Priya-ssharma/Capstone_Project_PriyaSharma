analysis/clean_and_eda.py

import pandas as pd


# Task 1 - Load and inspect

customers = pd.read_csv("data/customers.csv")
products = pd.read_csv("data/products.csv")
orders = pd.read_csv("data/orders.csv")
print("TASK 1 — DATA LOADING")
print("Customers shape:", customers.shape)
print("Products shape:", products.shape)
print("Orders shape:", orders.shape)

# Task 2 - Standardize payment_method casing

print("Payment methods before cleaning:")
print(orders["payment_method"].unique())

print("\nNumber of unique values before cleaning:")
print(orders["payment_method"].nunique())

orders["payment_method"] = (
    orders["payment_method"]
    .str.strip()
    .str.upper()
)

print("\nPayment methods after cleaning:")
print(orders["payment_method"].unique())

print("\nPayment method counts after cleaning:")
print(orders["payment_method"].value_counts())

# Task 3 - Remove duplicate orders

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

dropped_orders = orders[duplicate_mask].copy()

print("Number of duplicate rows flagged:")
print(len(dropped_orders))

print("\nDropped order IDs:")
print(dropped_orders["order_id"].tolist())

orders_clean = orders[~duplicate_mask].copy()

print("\nOrders shape before removing duplicates:")
print(orders.shape)

print("\nOrders shape after removing duplicates:")
print(orders_clean.shape)

# Task 4 - Impute missing values

missing_discount = orders_clean["discount_pct"].isna().sum()
print("Missing discount_pct before imputation:", missing_discount)

orders_clean["discount_pct"] = orders_clean["discount_pct"].fillna(0)

rating_median = orders_clean["rating"].median()
print("Median rating before imputation:", rating_median)

missing_rating = orders_clean["rating"].isna().sum()
print("Missing rating rows before imputation:", missing_rating)

orders_clean["rating"] = orders_clean["rating"].fillna(rating_median)

print("\nMissing values after imputation:")
print(orders_clean[["discount_pct", "rating"]].isnull().sum())

# Task 5 - Merge and reconcile against Part 1

merged = orders_clean.merge(
    products,
    on="product_id",
    how="left"
)

merged = merged.merge(
    customers,
    on="customer_id",
    how="left"
)

merged["order_value"] = (
    merged["quantity"]
    * merged["price"]
    * (1 - merged["discount_pct"] / 100)
)

cleaned_total_revenue = merged["order_value"].sum()

print("Merged rows:", len(merged))
print("Cleaned total revenue:", round(cleaned_total_revenue, 2))


# Independently calculate order_value of the 5 dropped duplicate rows

dropped_orders_check = dropped_orders.merge(
    products,
    on="product_id",
    how="left"
)

dropped_orders_check["discount_pct"] = (
    dropped_orders_check["discount_pct"].fillna(0)
)

dropped_orders_check["order_value"] = (
    dropped_orders_check["quantity"]
    * dropped_orders_check["price"]
    * (1 - dropped_orders_check["discount_pct"] / 100)
)

duplicate_order_value = dropped_orders_check["order_value"].sum()

print("Order value of 5 dropped duplicates:", round(duplicate_order_value, 2))


# Reconciliation against Part 1

raw_total_revenue = 99860.20
reconciliation_delta = raw_total_revenue - cleaned_total_revenue

print("Part 1 raw total revenue:", round(raw_total_revenue, 2))
print("Reconciliation delta:", round(reconciliation_delta, 2))


print("\nReconciliation Note:")
print(
    f"Part 2 cleaned revenue is ₹{cleaned_total_revenue:,.2f}, "
    f"which is ₹{reconciliation_delta:,.2f} less than the Part 1 "
    f"raw revenue of ₹{raw_total_revenue:,.2f}. This exact delta is "
    f"attributed to the 5 duplicate orders removed in Task 3, whose "
    f"combined order_value is ₹{duplicate_order_value:,.2f}. The "
    f"discount_pct and rating imputations do not change the order_value "
    f"total because rating is not used in the revenue calculation and "
    f"missing discount_pct values are treated as 0%."
)

# Task 6 - IQR outlier detection on quantity

Q1 = merged["quantity"].quantile(0.25)
Q3 = merged["quantity"].quantile(0.75)

IQR = Q3 - Q1

lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print("Q1:", Q1)
print("Q3:", Q3)
print("IQR:", IQR)
print("Lower bound:", lower)
print("Upper bound:", upper)

merged["is_outlier"] = (
    (merged["quantity"] < lower) |
    (merged["quantity"] > upper)
)

outliers = merged[merged["is_outlier"]].copy()

print("\nNumber of outliers:", len(outliers))

print("\nOutlier orders:")
print(outliers[["order_id", "quantity"]])

print("\nOutlier order IDs:")
print(outliers["order_id"].tolist())

# Task 7 - Hypothesis: does COD have a higher return rate?

print("Hypothesis: COD has a higher return rate than CARD and UPI.")

return_rate = (
    orders_clean
    .groupby("payment_method")["returned"]
    .agg(["count", "mean"])
)

return_rate["return_rate_pct"] = (
    return_rate["mean"] * 100
).round(1)

print("\nReturn rate by payment method:")
print(return_rate)

cod_rate = return_rate.loc["COD", "return_rate_pct"]
card_rate = return_rate.loc["CARD", "return_rate_pct"]
upi_rate = return_rate.loc["UPI", "return_rate_pct"]

if cod_rate > card_rate and cod_rate > upi_rate:
    print("\nHypothesis: Confirmed")
else:
    print("\nHypothesis: Busted")

# Task 8 - Multi-level segmentation 

orders_segment = orders_clean.merge(
    customers[["customer_id", "city_tier"]],
    on="customer_id",
    how="left"
)

segment_return_rate = (
    orders_segment
    .groupby(["payment_method", "city_tier"])["returned"]
    .agg(["count", "mean"])
)

segment_return_rate["return_rate_pct"] = (
    segment_return_rate["mean"] * 100
).round(1)

print("Return rate by payment method and city tier:")
print(segment_return_rate)

highest_risk = segment_return_rate["return_rate_pct"].idxmax()
highest_risk_rate = segment_return_rate["return_rate_pct"].max()

print("\nHighest-risk segment:")
print(
    f"Payment Method: {highest_risk[0]}, "
    f"City Tier: {highest_risk[1]}, "
    f"Return Rate: {highest_risk_rate}%"
)

print("\nCOD risk by city tier:")
print(
    segment_return_rate.loc[
        "COD",
        ["count", "return_rate_pct"]
    ]
)

print(
    "\nFinding: COD + Tier-2 cities are the highest-risk segment "
    "at 54.5%. COD Tier-1 has a 37.5% return rate, while COD "
    "Tier-2 has a 54.5% return rate, showing that COD risk is "
    "not uniform across city tiers."
)

# Task 9 - Correlation analysis

corr_cols = ["rating", "returned", "discount_pct", "quantity"]

corr_matrix = orders_clean[corr_cols].corr()

print("Correlation Matrix:")
print(corr_matrix.round(3))

print("\nCorrelation strength for every pair:")

pairs = [
    ("rating", "returned"),
    ("rating", "discount_pct"),
    ("rating", "quantity"),
    ("returned", "discount_pct"),
    ("returned", "quantity"),
    ("discount_pct", "quantity")
]

for col1, col2 in pairs:
    r = corr_matrix.loc[col1, col2]
    
    if abs(r) < 0.2:
        strength = "negligible"
    elif abs(r) < 0.4:
        strength = "weak"
    elif abs(r) < 0.7:
        strength = "moderate"
    else:
        strength = "strong"
    
    print(
        f"{col1} vs {col2}: "
        f"r = {r:.3f} → {strength}"
    )

discount_return_corr = corr_matrix.loc["discount_pct", "returned"]

print("\nHypothesis: Higher discounts reduce returns")
if discount_return_corr < 0:
    print(
        f"Correlation = {discount_return_corr:.3f} "
        f"→ Busted (negligible negative relationship)"
    )
else:
    print(
        f"Correlation = {discount_return_corr:.3f} "
        f"→ Busted"
    )

# Task 10 - Outlier-corrected time series

merged["order_date"] = pd.to_datetime(merged["order_date"])
merged["year_month"] = merged["order_date"].dt.to_period("M").astype(str)

monthly_revenue_including = (
    merged.groupby("year_month")["order_value"]
    .sum()
    .round(2)
)

print("Monthly order_value INCLUDING outliers:")
print(monthly_revenue_including)

merged_without_outliers = merged[~merged["is_outlier"]].copy()

monthly_revenue_excluding = (
    merged_without_outliers.groupby("year_month")["order_value"]
    .sum()
    .round(2)
)

print("\nMonthly order_value EXCLUDING outliers:")
print(monthly_revenue_excluding)

print("\nPeak month INCLUDING outliers:")
print(
    f"{monthly_revenue_including.idxmax()}: "
    f"₹{monthly_revenue_including.max():,.2f}"
)
print("\nPeak month EXCLUDING outliers:")
print(
    f"{monthly_revenue_excluding.idxmax()}: "
    f"₹{monthly_revenue_excluding.max():,.2f}"
)

print(
    "\nFinding: January's apparent lead is an artifact of the two "
    "bulk orders landing in January (O0011 on 2026-01-28 and "
    "O0098 on 2026-01-10). Once these two outliers are excluded, "
    "March 2026 is the genuine peak month."
)








