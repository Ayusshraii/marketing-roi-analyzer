"""
data_prep.py
============
- Cleans raw campaign CSV data
- Computes derived KPI columns
- Optionally generates synthetic sample data for demo purposes
- Saves processed output to data/processed/

Usage:
    python src/data_prep.py                     # Clean raw data
    python src/data_prep.py --generate-sample   # Generate sample CSV
"""

import os
import argparse
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# ── Config ────────────────────────────────────────────────────
RAW_PATH       = "data/raw/sample_campaigns.csv"
PROCESSED_PATH = "data/processed/campaigns_clean.csv"

PLATFORMS    = ["Meta", "Google", "Instagram"]
CATEGORIES   = ["Fashion", "Electronics", "Food & Beverage", "Health & Wellness"]
VARIANT_COPY = {
    "A": {
        "headline": "Last 48 Hours: Up to 50% Off — Shop Now",
        "body":     "Don't miss out. Our biggest sale ends soon. Free shipping on all orders above ₹499.",
        "cta":      "Shop Now"
    },
    "B": {
        "headline": "Brand Name — Quality You Can Trust",
        "body":     "Discover our latest collection. Premium quality, fair prices.",
        "cta":      "Learn More"
    },
    "C": {
        "headline": "Over 10,000 Happy Customers Can't Be Wrong",
        "body":     "Join thousands who've transformed their routine. Rated 4.8/5 stars.",
        "cta":      "See Reviews"
    },
    "D": {
        "headline": "Only 3 Left in Stock — Order Before It's Gone",
        "body":     "High demand item. Secure yours before stock runs out. Fast delivery guaranteed.",
        "cta":      "Buy Now"
    },
    "E": {
        "headline": "Get 20% Off Your First Order",
        "body":     "New here? Use code FIRST20 at checkout. Limited time offer.",
        "cta":      "Claim Offer"
    },
}

# Simulated performance multipliers per copy variant
ROAS_MULTIPLIER = {"A": 3.8, "B": 1.2, "C": 3.1, "D": 4.1, "E": 2.5}
CTR_MULTIPLIER  = {"A": 0.042, "B": 0.011, "C": 0.037, "D": 0.048, "E": 0.029}


def generate_sample_data(n_campaigns=5, days=30, seed=42):
    """Generate synthetic campaign data for demo."""
    random.seed(seed)
    np.random.seed(seed)

    records = []
    start_date = datetime(2024, 1, 1)

    for camp_i in range(1, n_campaigns + 1):
        campaign_id = f"CAMP_{camp_i:03d}"
        platform    = random.choice(PLATFORMS)
        category    = random.choice(CATEGORIES)

        for variant, copy in VARIANT_COPY.items():
            creative_id = f"{campaign_id}_VAR_{variant}"
            base_impr   = random.randint(8000, 25000)

            for day in range(days):
                date = start_date + timedelta(days=day)
                impressions = int(base_impr / days * np.random.normal(1.0, 0.15))
                impressions = max(impressions, 0)

                ctr         = CTR_MULTIPLIER[variant] * np.random.normal(1.0, 0.1)
                clicks      = int(impressions * ctr)
                conv_rate   = random.uniform(0.02, 0.06)
                conversions = int(clicks * conv_rate)
                avg_order   = random.uniform(400, 1800)
                revenue     = round(conversions * avg_order, 2)
                cpc         = random.uniform(8, 35)
                spend       = round(clicks * cpc, 2)

                records.append({
                    "campaign_id":     campaign_id,
                    "campaign_name":   f"Campaign {camp_i} — {category}",
                    "platform":        platform,
                    "product_category": category,
                    "creative_id":     creative_id,
                    "variant":         variant,
                    "headline":        copy["headline"],
                    "body_copy":       copy["body"],
                    "cta":             copy["cta"],
                    "metric_date":     date.strftime("%Y-%m-%d"),
                    "impressions":     impressions,
                    "clicks":          clicks,
                    "conversions":     conversions,
                    "spend":           spend,
                    "revenue":         revenue,
                })

    df = pd.DataFrame(records)
    os.makedirs("data/raw", exist_ok=True)
    df.to_csv(RAW_PATH, index=False)
    print(f"✅ Sample data generated → {RAW_PATH}  ({len(df)} rows)")
    return df


def clean_and_enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Clean raw data and compute KPI columns."""
    df = df.copy()

    # Types
    df["metric_date"]  = pd.to_datetime(df["metric_date"])
    df["impressions"]  = pd.to_numeric(df["impressions"], errors="coerce").fillna(0).astype(int)
    df["clicks"]       = pd.to_numeric(df["clicks"],      errors="coerce").fillna(0).astype(int)
    df["conversions"]  = pd.to_numeric(df["conversions"], errors="coerce").fillna(0).astype(int)
    df["spend"]        = pd.to_numeric(df["spend"],        errors="coerce").fillna(0.0)
    df["revenue"]      = pd.to_numeric(df["revenue"],      errors="coerce").fillna(0.0)

    # Derived KPIs
    df["ctr_pct"]       = (df["clicks"] / df["impressions"].replace(0, np.nan) * 100).round(2)
    df["cpc"]           = (df["spend"]  / df["clicks"].replace(0, np.nan)).round(2)
    df["roas"]          = (df["revenue"]/ df["spend"].replace(0, np.nan)).round(2)
    df["conv_rate_pct"] = (df["conversions"] / df["clicks"].replace(0, np.nan) * 100).round(2)

    # Drop rows where both clicks and impressions are 0
    df = df[~((df["impressions"] == 0) & (df["clicks"] == 0))]

    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"✅ Cleaned data saved → {PROCESSED_PATH}  ({len(df)} rows)")
    return df


def aggregate_by_creative(df: pd.DataFrame) -> pd.DataFrame:
    """Roll up daily rows to creative-level totals."""
    agg = df.groupby(
        ["campaign_id", "creative_id", "variant", "headline", "body_copy", "cta"],
        as_index=False
    ).agg(
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        spend=("spend", "sum"),
        revenue=("revenue", "sum"),
    )

    agg["ctr_pct"]       = (agg["clicks"] / agg["impressions"].replace(0, np.nan) * 100).round(2)
    agg["roas"]          = (agg["revenue"] / agg["spend"].replace(0, np.nan)).round(2)
    agg["conv_rate_pct"] = (agg["conversions"] / agg["clicks"].replace(0, np.nan) * 100).round(2)

    agg = agg.sort_values("roas", ascending=False)
    return agg


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate-sample", action="store_true", help="Generate synthetic sample data")
    args = parser.parse_args()

    if args.generate_sample or not os.path.exists(RAW_PATH):
        df_raw = generate_sample_data()
    else:
        df_raw = pd.read_csv(RAW_PATH)
        print(f"📂 Loaded raw data: {len(df_raw)} rows")

    df_clean = clean_and_enrich(df_raw)

    creative_summary = aggregate_by_creative(df_clean)
    summary_path = "data/processed/creative_summary.csv"
    creative_summary.to_csv(summary_path, index=False)
    print(f"✅ Creative summary saved → {summary_path}")
    print("\nTop 5 creatives by ROAS:")
    print(creative_summary[["campaign_id", "variant", "headline", "roas", "ctr_pct"]].head())
