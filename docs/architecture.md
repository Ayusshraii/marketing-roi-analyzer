# Project Architecture

## Data Flow

```
Raw CSV Data
     │
     ▼
data_prep.py ──────────────────────────────────────────────────
     │  • Cleans & validates raw campaign data                 │
     │  • Computes CTR, ROAS, CPC, Conv Rate                  │
     │  • Saves: data/processed/campaigns_clean.csv            │
     │           data/processed/creative_summary.csv           │
     ▼
ab_test.py ─────────────────────────────────────────────────────
     │  • Chi-squared test per campaign (top vs bottom)        │
     │  • Flags statistically significant differences          │
     │  • Saves: data/processed/ab_test_results.csv            │
     ▼
ai_diagnosis.py ────────────────────────────────────────────────
     │  • Pulls top 2 + bottom 2 creatives per campaign        │
     │  • Builds structured prompt with metrics + copy         │
     │  • Calls Claude API (claude-sonnet-4-20250514)          │
     │  • Saves: outputs/ai_diagnosis_report.md                │
     ▼
report_generator.py ───────────────────────────────────────────
     │  • Combines all processed data                          │
     │  • Builds 3-sheet formatted Excel report                │
     │  • Saves: outputs/campaign_report.xlsx                  │
     ▼
Power BI Dashboard
     • Connects to: data/processed/creative_summary.csv
     • Visualizes: KPIs, trends, platform comparison
```

## Key Design Decisions

### Why Claude API for copy diagnosis?
- Rule-based approaches (keyword matching) miss nuanced patterns
- LLMs understand copywriting psychology, not just keywords
- Output is human-readable and immediately actionable

### Why chi-squared for A/B testing?
- Conversion rate comparison is a proportion test → chi-squared is correct
- More appropriate than t-test for count/rate data
- Industry standard for digital marketing A/B testing

### Why separate scripts vs. a single pipeline?
- Easier to debug and iterate on individual components
- Allows partial runs (e.g., re-run AI diagnosis without re-processing data)
- Clean separation of concerns for portfolio clarity

## MySQL Schema Overview

```
campaigns ─────┐
               ├── ad_creatives ──── campaign_metrics
               └── ai_diagnoses
```
