# Mamaearth Returns & Growth Intelligence Pipeline

## Project Overview

This project analyzes Mamaearth customer, product, and order data to identify revenue trends, return risks, data-quality issues, and actionable business insights.

**Pipeline:** SQL → Python/Pandas EDA → Visualization → GenAI-powered SCR narrative

[View Interactive GitDiagram](https://gitdiagram.com/priya-ssharma/capstone_project_priyasharma)

## Technologies Used

- **Database:** MySQL
- **Programming:** Python, Pandas
- **Visualization:** Matplotlib
- **Data Formats:** CSV, JSON
- **GenAI:** Google Gemini API
- **Version Control:** Git, GitHub

## Project Structure

```text
analysis/       # Data cleaning, EDA and visualizations
data/           # Customer, product and order CSV files
narrator/       # Findings, SCR narrative and generator
sql/            # Schema, seed data and analytical queries
visualizations/ # Generated charts
```

## Part 1 — SQL Analysis

Run these files in order using MySQL:

1. `sql/schema.sql` — Create tables.
2. `sql/seed_data.sql` — Load data.
3. `sql/reports.sql` — Execute analytical queries.

## Part 2 — Python EDA and Visualization

Run from the project root:

```bash
python analysis/clean_and_eda.py
python analysis/visualize.py
```

The analysis standardizes payment methods, handles duplicates and missing values, calculates revenue, identifies quantity outliers, analyzes returns, and generates monthly trends.

Key outputs:

- `narrator/findings.json`
- `visualizations/return_rate_by_payment.png`
- `visualizations/monthly_revenue_trend.png`

## Part 3 — GenAI Business Narrator

The narrator uses verified findings from `narrator/findings.json` to create a Situation–Complication–Resolution (SCR) business narrative.

**Configured model:** `gemini-3.8-flash`

Set the `GEMINI_API_KEY` environment variable before running the narrator. In Google Colab, use Colab Secrets or a secure input prompt. Never commit API keys to GitHub.

Run:

```bash
python narrator/generate_narrative.py
```

If the API key is missing or Gemini is unavailable, the script uses a deterministic offline fallback.

The output is saved to `narrator/sample_output.txt`. The saved narrative passed all five required numeric accuracy checks in Google Colab using the offline fallback. Successful Gemini-generated output remains dependent on API availability.

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
3. **Data quality:** Duplicate records account for a ₹2,501.90 revenue reconciliation delta.
4. **Revenue trends:** After correcting for quantity outliers, March 2026 is the peak month at ₹20,318.90.

## Recommendations

- Investigate COD return drivers, particularly in Tier-2 cities.
- Review order-confirmation and delivery processes.
- Maintain duplicate detection and reconciliation controls.
- Use cleaned data for financial reporting.
- Monitor revenue trends alongside outlier flags.

These recommendations should be validated against additional operational data before implementation.

## End-to-End Workflow

1. Execute the three SQL files in order.
2. Run `python analysis/clean_and_eda.py`.
3. Verify `narrator/findings.json`.
4. Run `python analysis/visualize.py`.
5. Run `python narrator/generate_narrative.py`.
6. Verify the five numeric checks and review `narrator/sample_output.txt`.
