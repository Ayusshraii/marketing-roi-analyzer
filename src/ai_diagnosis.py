"""
ai_diagnosis.py
===============
Core Gen AI layer of the project.
Sends top vs bottom performing ad copy data to Gemini API
and receives a plain-English marketing diagnosis.

Usage:
    python src/ai_diagnosis.py
"""

import os
import pandas as pd
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUMMARY_PATH = "data/processed/creative_summary.csv"
OUTPUT_PATH  = "outputs/ai_diagnosis_report.md"

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash")


def build_prompt(campaign_id: str, top_creatives: list, bottom_creatives: list) -> str:
    """Build the structured prompt for Gemini."""

    top_section = "\n".join([
        f"  - Variant {c['variant']}: ROAS={c['roas']}x | CTR={c['ctr_pct']}% | CVR={c['conv_rate_pct']}%\n"
        f"    Headline: \"{c['headline']}\"\n"
        f"    Body: \"{c['body_copy']}\"\n"
        f"    CTA: \"{c['cta']}\""
        for c in top_creatives
    ])

    bottom_section = "\n".join([
        f"  - Variant {c['variant']}: ROAS={c['roas']}x | CTR={c['ctr_pct']}% | CVR={c['conv_rate_pct']}%\n"
        f"    Headline: \"{c['headline']}\"\n"
        f"    Body: \"{c['body_copy']}\"\n"
        f"    CTA: \"{c['cta']}\""
        for c in bottom_creatives
    ])

    return f"""You are a senior digital marketing strategist with 10+ years of experience analyzing ad performance.

I have campaign performance data for {campaign_id}. Below are the top-performing and bottom-performing ad creatives based on ROAS (Return on Ad Spend).

## TOP PERFORMERS
{top_section}

## BOTTOM PERFORMERS
{bottom_section}

## Your Task
Analyze the copy differences between top and bottom performers. Provide:

1. **Key Copy Patterns** — What specific language, structure, or messaging techniques appear in top performers that are absent in bottom performers?

2. **Psychological Triggers** — Which psychological triggers (urgency, social proof, scarcity, benefit-led, etc.) are driving the performance gap?

3. **CTA Analysis** — How do the calls-to-action differ and what impact does this have?

4. **3 Actionable Recommendations** — Specific, implementable changes the marketing team can make to improve the underperforming ads.

5. **Predicted Impact** — If recommendations are implemented, what % improvement in CTR or ROAS would you estimate?

Be specific, concise, and data-driven. Avoid generic marketing advice."""


def diagnose_campaign(campaign_id: str, df: pd.DataFrame) -> str:
    """Run Gemini diagnosis for a single campaign."""
    camp_df = df[df["campaign_id"] == campaign_id].sort_values("roas", ascending=False)

    if len(camp_df) < 2:
        return f"Not enough creative variants for campaign {campaign_id}."

    top_n    = camp_df.head(2).to_dict(orient="records")
    bottom_n = camp_df.tail(2).to_dict(orient="records")

    prompt   = build_prompt(campaign_id, top_n, bottom_n)
    response = model.generate_content(prompt)

    return response.text


def run_all_diagnoses(df: pd.DataFrame) -> dict:
    """Run diagnosis for all unique campaigns."""
    diagnoses = {}
    campaigns = df["campaign_id"].unique()

    print(f"\n🤖 Running Gemini AI diagnosis for {len(campaigns)} campaigns...\n")

    for i, campaign_id in enumerate(campaigns, 1):
        print(f"  [{i}/{len(campaigns)}] Analyzing {campaign_id}...")
        try:
            diagnosis = diagnose_campaign(campaign_id, df)
            diagnoses[campaign_id] = diagnosis
            print(f"  ✅ Done")
        except Exception as e:
            diagnoses[campaign_id] = f"Error: {str(e)}"
            print(f"  ❌ Error: {e}")

    return diagnoses


def save_report(diagnoses: dict):
    """Save all diagnoses as a Markdown report."""
    os.makedirs("outputs", exist_ok=True)

    lines = [
        "# 🤖 AI Campaign Copy Diagnosis Report",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}  |  Model: Gemini 1.5 Flash",
        "",
        "---",
        "",
    ]

    for campaign_id, diagnosis in diagnoses.items():
        lines += [
            f"## Campaign: {campaign_id}",
            "",
            diagnosis,
            "",
            "---",
            "",
        ]

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n✅ AI diagnosis report saved → {OUTPUT_PATH}")


if __name__ == "__main__":
    df       = pd.read_csv(SUMMARY_PATH)
    diagnoses = run_all_diagnoses(df)
    save_report(diagnoses)

    first_key = list(diagnoses.keys())[0]
    print(f"\n📋 Preview — {first_key}:\n")
    print(diagnoses[first_key][:800] + "...")