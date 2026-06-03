"""
ab_test.py
==========
Statistical A/B test analysis on ad creative variants.
Uses chi-squared test for conversion rate significance.

Usage:
    python src/ab_test.py
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

SUMMARY_PATH = "data/processed/creative_summary.csv"


def run_ab_test(control: pd.Series, treatment: pd.Series) -> dict:
    """
    Chi-squared test comparing conversion rates.
    control / treatment: rows with clicks & conversions columns.
    """
    table = [
        [control["conversions"],   control["clicks"]   - control["conversions"]],
        [treatment["conversions"], treatment["clicks"] - treatment["conversions"]],
    ]
    chi2, p_value, _, _ = stats.chi2_contingency(table)

    lift = (
        (treatment["conv_rate_pct"] - control["conv_rate_pct"])
        / control["conv_rate_pct"] * 100
        if control["conv_rate_pct"] > 0 else None
    )

    return {
        "chi2_stat":      round(chi2, 4),
        "p_value":        round(p_value, 4),
        "significant":    p_value < 0.05,
        "lift_pct":       round(lift, 2) if lift else None,
        "control_cvr":    round(control["conv_rate_pct"], 2),
        "treatment_cvr":  round(treatment["conv_rate_pct"], 2),
    }


def analyze_all_campaigns(df: pd.DataFrame):
    results = []

    for campaign_id, group in df.groupby("campaign_id"):
        group = group.sort_values("roas", ascending=False).reset_index(drop=True)

        if len(group) < 2:
            continue

        top    = group.iloc[0]   # best ROAS = treatment
        bottom = group.iloc[-1]  # worst ROAS = control

        test   = run_ab_test(control=bottom, treatment=top)

        results.append({
            "campaign_id":       campaign_id,
            "top_variant":       top["variant"],
            "top_headline":      top["headline"][:60] + "...",
            "top_roas":          top["roas"],
            "bottom_variant":    bottom["variant"],
            "bottom_headline":   bottom["headline"][:60] + "...",
            "bottom_roas":       bottom["roas"],
            **test,
        })

    return pd.DataFrame(results)


def print_report(results: pd.DataFrame):
    print("\n" + "=" * 70)
    print("  A/B TEST ANALYSIS REPORT — Campaign Creative Performance")
    print("=" * 70)

    for _, row in results.iterrows():
        sig_label = "✅ SIGNIFICANT" if row["significant"] else "⚠️  NOT SIGNIFICANT"
        print(f"\n📌 Campaign: {row['campaign_id']}")
        print(f"   Top:    Variant {row['top_variant']} | ROAS: {row['top_roas']}x | CVR: {row['treatment_cvr']}%")
        print(f"           \"{row['top_headline']}\"")
        print(f"   Bottom: Variant {row['bottom_variant']} | ROAS: {row['bottom_roas']}x | CVR: {row['control_cvr']}%")
        print(f"           \"{row['bottom_headline']}\"")
        print(f"   Result: {sig_label} | p-value: {row['p_value']} | Lift: {row['lift_pct']}%")

    print("\n" + "=" * 70)
    sig_count = results["significant"].sum()
    print(f"  {sig_count}/{len(results)} campaigns show statistically significant differences")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    df = pd.read_csv(SUMMARY_PATH)
    results = analyze_all_campaigns(df)
    print_report(results)

    out_path = "data/processed/ab_test_results.csv"
    results.to_csv(out_path, index=False)
    print(f"✅ A/B test results saved → {out_path}")
