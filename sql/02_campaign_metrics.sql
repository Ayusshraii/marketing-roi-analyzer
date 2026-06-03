-- ============================================================
-- 02_campaign_metrics.sql
-- Core KPI calculations per campaign and creative
-- ============================================================

USE marketing_roi;

-- ── 1. Overall Campaign Performance Summary ──────────────────
SELECT
    c.campaign_id,
    c.campaign_name,
    c.platform,
    SUM(m.impressions)                              AS total_impressions,
    SUM(m.clicks)                                   AS total_clicks,
    SUM(m.conversions)                              AS total_conversions,
    SUM(m.spend)                                    AS total_spend,
    SUM(m.revenue)                                  AS total_revenue,
    ROUND(SUM(m.clicks) / NULLIF(SUM(m.impressions), 0) * 100, 2)  AS ctr_pct,
    ROUND(SUM(m.spend)  / NULLIF(SUM(m.clicks), 0), 2)             AS cpc,
    ROUND(SUM(m.revenue)/ NULLIF(SUM(m.spend), 0), 2)              AS roas,
    ROUND(SUM(m.conversions) / NULLIF(SUM(m.clicks), 0) * 100, 2)  AS conv_rate_pct
FROM campaigns c
JOIN campaign_metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.campaign_id, c.campaign_name, c.platform
ORDER BY roas DESC;


-- ── 2. Creative-Level Performance (for AI diagnosis input) ───
SELECT
    ac.creative_id,
    ac.variant_name,
    ac.headline,
    ac.body_copy,
    ac.cta_text,
    SUM(m.impressions)                                              AS impressions,
    SUM(m.clicks)                                                   AS clicks,
    SUM(m.conversions)                                              AS conversions,
    SUM(m.spend)                                                    AS spend,
    SUM(m.revenue)                                                  AS revenue,
    ROUND(SUM(m.clicks) / NULLIF(SUM(m.impressions), 0) * 100, 2)  AS ctr_pct,
    ROUND(SUM(m.revenue)/ NULLIF(SUM(m.spend), 0), 2)              AS roas
FROM ad_creatives ac
JOIN campaign_metrics m ON ac.creative_id = m.creative_id
GROUP BY ac.creative_id, ac.variant_name, ac.headline, ac.body_copy, ac.cta_text
ORDER BY roas DESC;


-- ── 3. Daily Trend — Spend vs Revenue ────────────────────────
SELECT
    metric_date,
    SUM(spend)   AS daily_spend,
    SUM(revenue) AS daily_revenue,
    ROUND(SUM(revenue) / NULLIF(SUM(spend), 0), 2) AS daily_roas
FROM campaign_metrics
GROUP BY metric_date
ORDER BY metric_date;


-- ── 4. Platform Comparison ────────────────────────────────────
SELECT
    c.platform,
    COUNT(DISTINCT c.campaign_id)                                   AS num_campaigns,
    SUM(m.spend)                                                    AS total_spend,
    SUM(m.revenue)                                                  AS total_revenue,
    ROUND(SUM(m.revenue) / NULLIF(SUM(m.spend), 0), 2)             AS platform_roas,
    ROUND(SUM(m.clicks)  / NULLIF(SUM(m.impressions), 0) * 100, 2) AS avg_ctr
FROM campaigns c
JOIN campaign_metrics m ON c.campaign_id = m.campaign_id
GROUP BY c.platform
ORDER BY platform_roas DESC;
