-- ============================================================
-- 01_create_tables.sql
-- Marketing ROI Analyzer - Database Schema
-- ============================================================

CREATE DATABASE IF NOT EXISTS marketing_roi;
USE marketing_roi;

-- Campaigns master table
CREATE TABLE IF NOT EXISTS campaigns (
    campaign_id     VARCHAR(20) PRIMARY KEY,
    campaign_name   VARCHAR(100) NOT NULL,
    platform        ENUM('Meta', 'Google', 'Instagram') NOT NULL,
    product_category VARCHAR(50),
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    total_budget    DECIMAL(10, 2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Ad creatives table
CREATE TABLE IF NOT EXISTS ad_creatives (
    creative_id     VARCHAR(20) PRIMARY KEY,
    campaign_id     VARCHAR(20),
    variant_name    VARCHAR(10),          -- e.g. Variant A, B, C
    headline        VARCHAR(200),
    body_copy       TEXT,
    cta_text        VARCHAR(50),
    creative_type   ENUM('image', 'video', 'carousel'),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- Daily performance metrics
CREATE TABLE IF NOT EXISTS campaign_metrics (
    metric_id       INT AUTO_INCREMENT PRIMARY KEY,
    creative_id     VARCHAR(20),
    campaign_id     VARCHAR(20),
    metric_date     DATE NOT NULL,
    impressions     INT DEFAULT 0,
    clicks          INT DEFAULT 0,
    conversions     INT DEFAULT 0,
    spend           DECIMAL(10, 2) DEFAULT 0.00,
    revenue         DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (creative_id) REFERENCES ad_creatives(creative_id),
    FOREIGN KEY (campaign_id) REFERENCES campaigns(campaign_id)
);

-- AI diagnosis results (stored for audit/tracking)
CREATE TABLE IF NOT EXISTS ai_diagnoses (
    diagnosis_id    INT AUTO_INCREMENT PRIMARY KEY,
    campaign_id     VARCHAR(20),
    run_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    top_performers  TEXT,     -- JSON of top creative IDs
    bottom_performers TEXT,   -- JSON of bottom creative IDs
    ai_diagnosis    LONGTEXT, -- Full Claude API response
    model_used      VARCHAR(50)
);
