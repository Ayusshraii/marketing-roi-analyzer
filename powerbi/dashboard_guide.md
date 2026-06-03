# Power BI Dashboard Guide

## Data Source
Connect Power BI to: `data/processed/creative_summary.csv`

---

## Recommended Pages & Visuals

### Page 1 — Executive Overview
| Visual | Type | Fields |
|--------|------|--------|
| Total ROAS | Card | AVG(roas) |
| Total Revenue | Card | SUM(revenue) |
| Total Spend | Card | SUM(spend) |
| ROAS by Campaign | Bar Chart | campaign_id vs roas |
| Spend vs Revenue Trend | Line Chart | (if date column added) |

### Page 2 — Creative Performance
| Visual | Type | Fields |
|--------|------|--------|
| Top 10 Creatives by ROAS | Table | variant, headline, roas, ctr_pct |
| CTR by Variant | Column Chart | variant vs ctr_pct |
| Conversion Rate Scatter | Scatter | ctr_pct vs conv_rate_pct |

### Page 3 — A/B Test Summary
| Visual | Type | Fields |
|--------|------|--------|
| Significant vs Not | Donut | significant count |
| Lift % by Campaign | Bar | campaign_id vs lift_pct |
| p-value Distribution | Histogram | p_value |

---

## Key DAX Measures

```dax
-- Overall ROAS
Total ROAS = DIVIDE(SUM(creative_summary[revenue]), SUM(creative_summary[spend]))

-- Weighted CTR
Weighted CTR =
DIVIDE(SUM(creative_summary[clicks]), SUM(creative_summary[impressions])) * 100

-- Top Variant Flag
Is Top Performer =
VAR MaxROAS = MAXX(ALLEXCEPT(creative_summary, creative_summary[campaign_id]), [Total ROAS])
RETURN IF([Total ROAS] = MaxROAS, "Top", "Other")
```

---

## Filter Slicers to Add
- Campaign ID
- Platform (Meta / Google / Instagram)
- Product Category
- Date Range (if applicable)
