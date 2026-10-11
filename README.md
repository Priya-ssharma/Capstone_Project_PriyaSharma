# Mamaearth Returns & Growth Intelligence Pipeline

## Project Overview

This project analyzes Mamaearth customer, product, and order data to identify revenue trends, return risks, data-quality issues, and actionable business insights.

**Pipeline:** SQL → Python/Pandas EDA → Visualizations → GenAI Business Narration

## Architecture Diagram

[View Interactive GitDiagram](https://gitdiagram.com/priya-ssharma/capstone_project_priyasharma)

## Project Structure

```text
analysis/       # Data cleaning, EDA and visualization
data/           # Customer, product and order CSV files
narrator/       # Verified findings and SCR narrative
sql/            # Schema, seed data and analytical queries
visualizations/ # Generated charts
```

## Part 1 — SQL Analysis

Open MySQL Workbench and select or create the project database. Execute the following SQL files in order:

1. `sql/schema.sql` — Create the customer, product and order tables.
2. `sql/seed_data.sql` — Load the data.
3. `sql/reports.sql` — Run the analytical queries and reproduce the SQL reports.

## Part 2 — Python Data Cleaning, EDA and Visualization

Run these commands from the project root, in order:

```bash
python analysis/clean_and_eda.py
python analysis/visualize.py
```

The cleaning and EDA script standardizes payment methods, handles duplicate submissions and missing values, calculates revenue, identifies quantity outliers, and performs return-rate, segmentation, correlation, and monthly revenue analysis.

**Task 5 of Part 2 writes the verified analytical findings to `narrator/findings.json`.**

The visualization script generates:

- `visualizations/return_rate_by_payment.png`
- `visualizations/monthly_revenue_trend.png`

## Part 3 — GenAI-Powered SCR Narrative

The narrator reads `narrator/findings.json` and saves the Situation–Complication–Resolution (SCR) narrative to `narrator/sample_output.txt`.

Run from the project root:

```bash
python narrator/generate_narrative.py
```

### Option A — Using Gemini

Set the `GEMINI_API_KEY` environment variable before running the narrator.

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
python narrator/generate_narrative.py
```

**Google Colab:**

```python
import os
from getpass import getpass

os.environ["GEMINI_API_KEY"] = getpass("Enter Gemini API key: ")
```

Then execute:

```python
!python narrator/generate_narrative.py
```

Use your own API key and never commit it to GitHub.

**Configured model:** `gemini-3.8-flash` (must match the model in `narrator/generate_narrative.py`).

Gemini generation depends on API availability. If the request fails or returns an incomplete narrative, the script uses the offline fallback.

### Option B — Without a Gemini API Key

If `GEMINI_API_KEY` is not configured, the script uses a deterministic offline fallback. No Gemini API call is required.

```bash
python narrator/generate_narrative.py
```

The fallback generates the SCR narrative from the existing verified findings and saves it to `narrator/sample_output.txt`.

### Output Validation

Verify that all five required numeric checks pass and review the saved narrative.

## Verified Business Findings

| Metric | Result |
|---|---:|
| Cleaned revenue | ₹97,358.30 |
| Raw revenue | ₹99,860.20 |
| Duplicate reconciliation delta | ₹2,501.90 |
| COD return rate | 44.4% |
| CARD return rate | 14.7% |
| UPI return rate | 18.9% |
| Highest-risk segment | COD + Tier-2 |
| Highest-risk return rate | 54.5% |
| True peak month | March 2026 |
| March revenue | ₹20,318.90 |
| January apparent revenue | ₹29,582.10 |
| January corrected revenue | ₹11,637.10 |

## Key Business Insights

1. **COD returns:** COD has the highest payment-method return rate at 44.4%.
2. **Regional risk:** COD orders in Tier-2 cities have a 54.5% return rate.
3. **Data quality:** Duplicate records account for a ₹2,501.90 reconciliation delta.
4. **Revenue trends:** After quantity-outlier correction, March 2026 is the peak month at ₹20,318.90.

## Business Recommendations

- Investigate COD return drivers, especially in Tier-2 cities.
- Review order-confirmation and delivery processes.
- Maintain duplicate detection and reconciliation controls.
- Use cleaned data for financial reporting.
- Monitor revenue alongside outlier flags.

These recommendations should be validated against additional operational data before implementation.

## End-to-End Reproduction Checklist

Follow these steps in order:

1. Execute `sql/schema.sql`.
2. Execute `sql/seed_data.sql`.
3. Execute `sql/reports.sql`.
4. Run `python analysis/clean_and_eda.py`.
5. Verify `narrator/findings.json`.
6. Run `python analysis/visualize.py`.
7. Run `python narrator/generate_narrative.py`.
8. Confirm all five numeric checks pass.
9. Review `narrator/sample_output.txt`.

## Technologies Used

- **Database:** MySQL
- **Programming:** Python
- **Data Analysis:** Pandas
- **Visualization:** Matplotlib
- **Data Formats:** CSV and JSON
- **Generative AI:** Google Gemini API
- **Business Framework:** Situation–Complication–Resolution (SCR)
- **Version Control:** Git and GitHub
