-- ============================================================
-- 03_ab_test_analysis.sql
-- A/B Test Comparison — Top vs Bottom Creative Variants
-- ============================================================

USE marketing_roi;

-- ── 1. Head-to-Head Creative Variant Comparison ──────────────
SELECT
    ac.campaign_id,
    ac.variant_name,
    ac.headline,
    SUM(m.impressions)                                              AS impressions,
    SUM(m.clicks)                                                   AS clicks,
    ROUND(SUM(m.clicks) / NULLIF(SUM(m.impressions), 0) * 100, 2)  AS ctr_pct,
    SUM(m.conversions)                                              AS conversions,
    ROUND(SUM(m.conversions) / NULLIF(SUM(m.clicks), 0) * 100, 2)  AS conv_rate_pct,
    ROUND(SUM(m.revenue) / NULLIF(SUM(m.spend), 0), 2)             AS roas
FROM ad_creatives ac
JOIN campaign_metrics m ON ac.creative_id = m.creative_id
GROUP BY ac.campaign_id, ac.variant_name, ac.headline
ORDER BY ac.campaign_id, roas DESC;


-- ── 2. Flag Top and Bottom Performers per Campaign ───────────
WITH ranked AS (
    SELECT
        ac.campaign_id,
        ac.creative_id,
        ac.variant_name,
        ac.headline,
        ac.body_copy,
        ROUND(SUM(m.revenue) / NULLIF(SUM(m.spend), 0), 2) AS roas,
        ROUND(SUM(m.clicks)  / NULLIF(SUM(m.impressions), 0) * 100, 2) AS ctr_pct,
        RANK() OVER (PARTITION BY ac.campaign_id ORDER BY
            SUM(m.revenue) / NULLIF(SUM(m.spend), 0) DESC) AS roas_rank,
        COUNT(*) OVER (PARTITION BY ac.campaign_id)        AS total_variants
    FROM ad_creatives ac
    JOIN campaign_metrics m ON ac.creative_id = m.creative_id
    GROUP BY ac.campaign_id, ac.creative_id, ac.variant_name, ac.headline, ac.body_copy
)
SELECT
    campaign_id,
    creative_id,
    variant_name,
    headline,
    body_copy,
    roas,
    ctr_pct,
    CASE
        WHEN roas_rank = 1 THEN 'TOP PERFORMER'
        WHEN roas_rank = total_variants THEN 'BOTTOM PERFORMER'
        ELSE 'MID'
    END AS performance_tier
FROM ranked
ORDER BY campaign_id, roas_rank;
