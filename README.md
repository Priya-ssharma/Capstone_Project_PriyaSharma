# Mamaearth Returns & Growth Intelligence Pipeline

## Project Overview

This project analyzes Mamaearth customer, product, and order data to identify
revenue trends, return-risk patterns, data-quality issues, and business
insights.

The project uses three main stages:

1. SQL analysis
2. Python/Pandas data cleaning, EDA, and visualization
3. GenAI-powered business insight narration

---
## Architecture Diagram

[View Interactive GitDiagram](https://gitdiagram.com/priya-ssharma/capstone_project_priyasharma)

# Part 1 — SQL Analysis

## SQL Pipeline

The SQL pipeline uses the following files:

```text
sql/
├── schema.sql
├── seed_data.sql
└── reports.sql
```

Run the SQL files in this order:

1. `sql/schema.sql`
2. `sql/seed_data.sql`
3. `sql/reports.sql`

### Step 1 — Create the database tables

Run:

`sql/schema.sql`

This creates the required tables for customers, products, and orders.

### Step 2 — Load the data

Run:

`sql/seed_data.sql`

This loads the customer, product, and order data into the database.

### Step 3 — Run the SQL analysis

Run:

`sql/reports.sql`

This executes the analytical SQL queries used to generate the required
business reports.

---

# Part 2 — Python Data Cleaning, EDA and Visualization

## Data Cleaning and EDA

Run the Python cleaning and EDA script from the project root:

```bash
python analysis/clean_and_eda.py
```

The script performs:

- Payment-method standardization
- Duplicate detection and reconciliation
- Missing-value treatment
- Revenue calculation
- Quantity outlier identification
- Return-rate analysis
- Payment-method risk analysis
- Correlation analysis
- Monthly revenue analysis

### Verified Findings

Task 5 of Part 2 automatically writes the verified findings to:

`narrator/findings.json`

This file contains the verified values used by the GenAI narrator in Part 3.

## Visualizations

After running the cleaning and EDA script, run:

```bash
python analysis/visualize.py
```

This generates the following visualizations:

`visualizations/return_rate_by_payment.png`

`visualizations/monthly_revenue_trend.png`

---

# Part 3 — GenAI-Powered Insight Narrator

The GenAI narrator converts the verified findings from Part 2 into a
Situation–Complication–Resolution (SCR) business narrative.

The narrator reads the verified findings from:

`narrator/findings.json`

## Gemini API Key Path

Set the Gemini API key as the `GEMINI_API_KEY` environment variable.

For Windows PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Then run:

```bash
python narrator/generate_narrative.py
```

The script attempts to generate the SCR narrative using Gemini.

Never put the actual API key in the Python code or commit the API key to
GitHub.

## Offline Path — No API Key

The narrator can also be run without a Gemini API key.

Simply run:

```bash
python narrator/generate_narrative.py
```

If `GEMINI_API_KEY` is not configured, or if the Gemini API call fails, the
script automatically uses the deterministic offline fallback.

The offline fallback does not require an API key or network connection.

The generated narrative is saved to:

`narrator/sample_output.txt`

---

# Verified Business Findings

The verified Part 2 analysis produced the following results:

- Cleaned revenue: ₹97,358.30
- Raw revenue: ₹99,860.20
- Duplicate reconciliation delta: ₹2,501.90
- COD return rate: 44.4%
- CARD return rate: 14.7%
- UPI return rate: 18.9%
- Highest-risk segment: COD + Tier-2
- Highest-risk return rate: 54.5%
- True peak month: March 2026
- March revenue: ₹20,318.90
- January apparent revenue: ₹29,582.10
- January corrected revenue: ₹11,637.10

---

# Business Insights

COD has the highest return rate among the three payment methods analyzed.

The highest-risk segment is COD in Tier-2 cities, with a 54.5% return rate.

Duplicate records created a reconciliation delta of ₹2,501.90 between the raw
and cleaned revenue figures.

January initially appeared to be the highest-revenue month because of quantity
outliers. After correcting for the outliers, March 2026 was the true peak month
with revenue of ₹20,318.90.

These findings indicate that regional operations should prioritize COD return
risk, particularly in Tier-2 cities, while finance should use reconciled and
cleaned data for reporting.

---

# End-to-End Pipeline

The complete project can be reproduced in this order:

1. Run `sql/schema.sql`
2. Run `sql/seed_data.sql`
3. Run `sql/reports.sql`
4. Run `python analysis/clean_and_eda.py`
5. Confirm that `narrator/findings.json` has been generated
6. Run `python analysis/visualize.py`
7. Run `python narrator/generate_narrative.py`
8. Review `narrator/sample_output.txt`

The narrator can be run either with a Gemini API key or without a key using
the deterministic offline fallback.
