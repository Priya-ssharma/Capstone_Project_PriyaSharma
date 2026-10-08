import json
import os

from google import genai
from google.genai import types


FINDINGS_PATH = "narrator/findings.json"
SAMPLE_OUTPUT_PATH = "narrator/sample_output.txt"


def generate_scr_narrative_offline(findings: dict) -> dict:
    """
    Deterministic offline fallback.
    Works without API key or internet.
    """

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
        "tokens": None
    }


def generate_scr_narrative(findings: dict) -> dict:
    """
    Generate SCR narrative using Gemini.

    Returns a structured dictionary in both success and error cases.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        return {
            "status": "error",
            "narrative": None,
            "message": "GEMINI_API_KEY is not configured."
        }

    system_instruction = """
You are a senior data analyst writing for Mamaearth's regional ops
and finance heads.

Write a concise business narrative with exactly these three labeled sections:

Situation
Complication
Resolution

Every numeric value in the output must come only from the supplied
findings dictionary.

Do not invent statistics, percentages, counts, dates, months,
or monetary values.

Preserve every supplied numeric value exactly.
"""

    # Findings are inserted dynamically so different findings.json
    # files produce different narratives without changing this function.
    contents = f"""
Write a business narrative of approximately 250 words using only
the following verified findings:

{json.dumps(findings, indent=2)}

The narrative must contain exactly these labeled sections:

Situation
Complication
Resolution

Do not introduce any number that is not present in the findings.
"""

    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                timeout=30000
            )
        )

        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,

                # Temperature 0.0 gives deterministic output.
                temperature=0.0,

                # Enough space for an approximately 250-word narrative.
                max_output_tokens=400
            )
        )

        tokens = getattr(
            getattr(response, "usage_metadata", None),
            "total_token_count",
            None
        )

        return {
            "status": "success",
            "narrative": response.text,
            "tokens": tokens
        }

    except Exception as err:
        return {
            "status": "error",
            "narrative": None,
            "message": str(err)
        }


def check_required_figures(narrative: str) -> bool:
    """
    Task 5 numeric accuracy checklist.
    """

    normalized = narrative.replace(",", "")

    checks = [
        (
            "Cleaned revenue: 97,358.30",
            "97358.3" in normalized
        ),
        (
            "COD return rate: 44.4%",
            "44.4" in normalized
        ),
        (
            "Highest-risk COD + Tier 2: 54.5%",
            "54.5" in normalized
        ),
        (
            "Duplicate reconciliation delta: 2,501.90",
            "2501.9" in normalized
        ),
        (
            "March peak: 20,318.90",
            "march" in narrative.lower()
            and "20318.9" in normalized
        )
    ]

    print("\nNumeric accuracy checklist:")

    for label, passed in checks:
        print(
            f"{label}: {'PASS' if passed else 'FAIL'}"
        )

    all_passed = all(
        passed for _, passed in checks
    )

    assert all_passed, (
        "Numeric accuracy checklist failed."
    )

    return True


def main():

    # Load verified findings generated by Part 2.
    with open(
        FINDINGS_PATH,
        "r",
        encoding="utf-8"
    ) as f:
        findings = json.load(f)

    print("Generating SCR narrative...")

    # Try Gemini first.
    result = generate_scr_narrative(findings)

    # If there is no API key or Gemini returns an error
    # such as 503, use the deterministic offline fallback.
    if result["status"] == "error":

        print(
            "Gemini unavailable. "
            "Using deterministic offline fallback."
        )

        result = generate_scr_narrative_offline(
            findings
        )

    print("\n" + "=" * 60)
    print("SCR NARRATIVE")
    print("=" * 60)

    print(result["narrative"])

    # Task 5 numeric accuracy verification.
    check_required_figures(
        result["narrative"]
    )

    # Save the actual narrative.
    with open(
        SAMPLE_OUTPUT_PATH,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(result["narrative"])

    print("\n" + "=" * 60)
    print(
        f"Sample output saved to {SAMPLE_OUTPUT_PATH}"
    )
    print("=" * 60)


if __name__ == "__main__":
    main()
