
import json
import os
from pathlib import Path

from google import genai
from google.genai import types


PROJECT_ROOT = Path(__file__).resolve().parent.parent
FINDINGS_PATH = PROJECT_ROOT / "narrator" / "findings.json"
SAMPLE_OUTPUT_PATH = PROJECT_ROOT / "narrator" / "sample_output.txt"


def generate_scr_narrative_offline(findings):
    """Create a reliable narrative using verified findings."""

    cleaned = findings["cleaned_total_revenue_inr"]
    raw = findings["raw_total_revenue_inr"]
    delta = findings["duplicate_reconciliation_delta_inr"]
    rates = findings["return_rate_by_payment"]
    risk = findings["highest_risk_segment"]
    peak = findings["true_peak_month"]
    inflated = findings["outlier_inflated_month"]

    narrative = f"""
Situation

Mamaearth's verified analysis shows cleaned revenue of ₹{cleaned:,.2f}
against raw revenue of ₹{raw:,.2f}.

Complication

COD recorded a {rates["COD"]:.1f}% return rate, compared with
CARD at {rates["CARD"]:.1f}% and UPI at {rates["UPI"]:.1f}%.
The highest-risk segment was {risk["payment_method"]} in Tier-{risk["city_tier"]},
with a {risk["return_rate_pct"]:.1f}% return rate.

Duplicate records created a reconciliation delta of ₹{delta:,.2f}.
January appeared to generate ₹{inflated["apparent_revenue_inr"]:,.2f},
but its corrected revenue was ₹{inflated["corrected_revenue_inr"]:,.2f}
after excluding quantity outliers.

Resolution

Regional operations should prioritize COD risk in Tier-{risk["city_tier"]}.
Finance should use the cleaned figures and reconcile duplicate records
before final reporting.

The verified peak month was March ({peak["month"]}), with revenue of
₹{peak["revenue_inr"]:,.2f}.
"""

    return {
        "status": "success",
        "narrative": narrative.strip(),
        "tokens": None,
    }


def generate_scr_narrative(findings):
    """Try Gemini to generate the narrative."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "message": "GEMINI_API_KEY is not configured.",
        }

    prompt = f"""
Write a concise business narrative for Mamaearth regional operations
and finance using only these verified findings:

{json.dumps(findings, indent=2)}

Use exactly these three labeled sections:
Situation
Complication
Resolution

Include these exact numeric findings:
- Cleaned revenue: ₹97,358.30
- COD return rate: 44.4%
- Highest-risk segment return rate: 54.5%
- Duplicate reconciliation delta: ₹2,501.90
- March 2026 corrected peak revenue: ₹20,318.90

Also include the raw revenue, CARD and UPI return rates, and January
outlier correction. Do not invent figures.
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=30000),
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,
                max_output_tokens=700,
            ),
        )

        narrative = getattr(response, "text", None)

        if not narrative or not narrative.strip():
            return {
                "status": "error",
                "narrative": None,
                "message": "Gemini returned an empty response.",
            }

        return {
            "status": "success",
            "narrative": narrative.strip(),
            "tokens": getattr(
                getattr(response, "usage_metadata", None),
                "total_token_count",
                None,
            ),
        }

    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": str(err),
        }


def check_required_figures(narrative):
    """Validate the required figures in the narrative."""

    normalized = (
        narrative.replace(",", "")
        .replace("₹", "")
        .lower()
    )

    checks = [
        ("Cleaned revenue: 97,358.30", "97358.30" in normalized),
        ("COD return rate: 44.4%", "44.4%" in normalized),
        ("Highest-risk rate: 54.5%", "54.5%" in normalized),
        ("Reconciliation delta: 2,501.90", "2501.90" in normalized),
        (
            "March peak: 20,318.90",
            "march" in normalized and "20318.90" in normalized,
        ),
    ]

    print("\nNumeric accuracy checklist:")

    for label, passed in checks:
        print(f"{label}: {'PASS' if passed else 'FAIL'}")

    failed = [label for label, passed in checks if not passed]

    if failed:
        raise ValueError(
            "Narrative failed required checks: " + "; ".join(failed)
        )

    return True


def main():
    with open(FINDINGS_PATH, "r", encoding="utf-8") as file:
        findings = json.load(file)

    print("Generating SCR narrative...")
    result = generate_scr_narrative(findings)

    # Use the offline fallback if Gemini fails.
    if result["status"] == "error":
        print("Gemini unavailable; using offline fallback.")
        print("Reason:", result.get("message", "Unknown error"))
        result = generate_scr_narrative_offline(findings)

    # Validate Gemini output before accepting it.
    else:
        try:
            check_required_figures(result["narrative"])
        except ValueError as err:
            print("Gemini response incomplete:", err)
            print("Using offline fallback.")
            result = generate_scr_narrative_offline(findings)

    # Save the final narrative.
    SAMPLE_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SAMPLE_OUTPUT_PATH.write_text(
        result["narrative"].strip() + "\n",
        encoding="utf-8",
    )

    # Validate the actual saved file.
    saved_narrative = SAMPLE_OUTPUT_PATH.read_text(encoding="utf-8")

    print("\n" + "=" * 60)
    print("SAVED SCR NARRATIVE")
    print("=" * 60)
    print(saved_narrative)

    check_required_figures(saved_narrative)
    print("\nSUCCESS: Saved narrative passed all numeric accuracy checks.")


if __name__ == "__main__":
    main()
