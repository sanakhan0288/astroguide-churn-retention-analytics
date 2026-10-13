-- =====================================================================
-- AstroGuide AI - Customer Churn & Retention Diagnostics
-- File: sql/03_churn_analysis.sql
-- Description: In-depth analysis of churn drivers: acquisition channels,
--              plan retention, user tenure, and pre-churn telemetry.
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Acquisition Channels Ranked by Churn Rate
-- Business Question: Which marketing channels have the highest churn?
-- Concepts: INNER JOIN, GROUP BY, aggregate percentage calculation, ORDER BY.
-- ---------------------------------------------------------------------
SELECT 
    u.acquisition_channel,
    COUNT(u.user_id) AS total_users,
    SUM(c.churn_label) AS churned_users,
    COUNT(u.user_id) - SUM(c.churn_label) AS retained_users,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS churn_rate_pct,
    ROUND((1.0 - AVG(c.churn_label)) * 100.0, 2) AS retention_rate_pct
FROM users u
INNER JOIN churn_labels c ON u.user_id = c.user_id
GROUP BY u.acquisition_channel
ORDER BY churn_rate_pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 2: Subscription Plan Retention Comparison
-- Business Question: Which subscription plans retain users best?
-- Concepts: Multi-table JOIN (users, subscriptions, churn_labels),
--           CASE WHEN, COALESCE, GROUP BY.
-- ---------------------------------------------------------------------
SELECT 
    u.subscription_plan AS initial_plan,
    COUNT(u.user_id) AS cohort_size,
    SUM(c.churn_label) AS churned_count,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS churn_rate_pct,
    ROUND((1.0 - AVG(c.churn_label)) * 100.0, 2) AS retention_rate_pct,
    -- Average renewal count among enrolled subscribers
    ROUND(AVG(s.renewal_count), 2) AS avg_plan_renewals
FROM users u
INNER JOIN churn_labels c ON u.user_id = c.user_id
LEFT JOIN subscriptions s ON u.user_id = s.user_id
GROUP BY u.subscription_plan
ORDER BY churn_rate_pct DESC;


-- ---------------------------------------------------------------------
-- QUERY 3: Customer Tenure Analysis (Churned vs. Retained)
-- Business Question: What is the average tenure of churned versus retained users?
-- Concepts: Date math (julianday in SQLite), CTE, conditional aggregation.
-- ---------------------------------------------------------------------
WITH user_tenures AS (
    SELECT 
        u.user_id,
        u.signup_date,
        c.observation_cutoff_date,
        -- Calculate tenure in days up to observation cutoff
        CAST(ROUND(julianday(c.observation_cutoff_date) - julianday(u.signup_date)) AS INTEGER) AS tenure_days,
        c.churn_label
    FROM users u
    INNER JOIN churn_labels c ON u.user_id = c.user_id
)
SELECT 
    CASE WHEN churn_label = 1 THEN 'Churned Users' ELSE 'Retained Users' END AS customer_status,
    COUNT(user_id) AS user_count,
    ROUND(AVG(tenure_days), 1) AS avg_tenure_days,
    MIN(tenure_days) AS min_tenure_days,
    MAX(tenure_days) AS max_tenure_days
FROM user_tenures
GROUP BY churn_label;


-- ---------------------------------------------------------------------
-- QUERY 4: Feature Engagement Association with Retention
-- Business Question: Which app features are associated with higher retention?
-- Concepts: Pre-cutoff filtering (prevent leakage), user-level aggregation,
--           CTE, INNER JOIN, comparing active feature adoption.
-- ---------------------------------------------------------------------
WITH pre_cutoff_features AS (
    SELECT 
        ua.user_id,
        MAX(CASE WHEN ua.feature_name = 'Horoscope' THEN 1 ELSE 0 END) AS used_horoscope,
        MAX(CASE WHEN ua.feature_name = 'AI_Chat' THEN 1 ELSE 0 END) AS used_ai_chat,
        MAX(CASE WHEN ua.feature_name = 'Compatibility' THEN 1 ELSE 0 END) AS used_compatibility,
        MAX(CASE WHEN ua.feature_name = 'Tarot' THEN 1 ELSE 0 END) AS used_tarot
    FROM user_activity ua
    WHERE ua.event_date <= '2025-08-31'
    GROUP BY ua.user_id
)
SELECT 
    'AI Chat' AS feature_name,
    COUNT(pcf.user_id) AS adopters_count,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS adopter_churn_rate_pct
FROM pre_cutoff_features pcf
INNER JOIN churn_labels c ON pcf.user_id = c.user_id
WHERE pcf.used_ai_chat = 1

UNION ALL

SELECT 
    'Compatibility Report' AS feature_name,
    COUNT(pcf.user_id) AS adopters_count,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS adopter_churn_rate_pct
FROM pre_cutoff_features pcf
INNER JOIN churn_labels c ON pcf.user_id = c.user_id
WHERE pcf.used_compatibility = 1

UNION ALL

SELECT 
    'Tarot Reading' AS feature_name,
    COUNT(pcf.user_id) AS adopters_count,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS adopter_churn_rate_pct
FROM pre_cutoff_features pcf
INNER JOIN churn_labels c ON pcf.user_id = c.user_id
WHERE pcf.used_tarot = 1

UNION ALL

SELECT 
    'Daily Horoscope' AS feature_name,
    COUNT(pcf.user_id) AS adopters_count,
    ROUND(AVG(c.churn_label) * 100.0, 2) AS adopter_churn_rate_pct
FROM pre_cutoff_features pcf
INNER JOIN churn_labels c ON pcf.user_id = c.user_id
WHERE pcf.used_horoscope = 1
ORDER BY adopter_churn_rate_pct ASC;


-- ---------------------------------------------------------------------
-- QUERY 5: Prioritizing User Segments for Retention Interventions
-- Business Question: Which customer segments should be targeted for retention campaigns?
-- Concepts: Multi-dimensional segment aggregation, net revenue calculation,
--           identifying high-revenue / high-churn risk groups.
-- ---------------------------------------------------------------------
WITH user_financials AS (
    SELECT 
        u.user_id,
        u.acquisition_channel,
        u.subscription_plan,
        u.onboarding_completed,
        c.churn_label,
        COALESCE(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) -
                 SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END), 0) AS net_revenue
    FROM users u
    INNER JOIN churn_labels c ON u.user_id = c.user_id
    LEFT JOIN transactions t ON u.user_id = t.user_id
    GROUP BY u.user_id, u.acquisition_channel, u.subscription_plan, u.onboarding_completed, c.churn_label
)
SELECT 
    subscription_plan,
    CASE WHEN onboarding_completed = 1 THEN 'Onboarded' ELSE 'Not Onboarded' END AS onboarding_status,
    COUNT(user_id) AS segment_size,
    SUM(churn_label) AS churned_users,
    ROUND(AVG(churn_label) * 100.0, 2) AS churn_rate_pct,
    ROUND(SUM(net_revenue), 2) AS total_segment_net_revenue,
    ROUND(AVG(net_revenue), 2) AS avg_revenue_per_user,
    CASE 
        WHEN AVG(churn_label) >= 0.50 AND SUM(net_revenue) > 20000 THEN 'CRITICAL: High Revenue, High Churn (Target Urgently)'
        WHEN AVG(churn_label) >= 0.50 THEN 'HIGH CHURN: Onboarding Intervention Needed'
        WHEN SUM(net_revenue) > 30000 THEN 'HEALTHY: High Value, Retain with Loyalty Perks'
        ELSE 'STANDARD'
    END AS strategic_priority
FROM user_financials
GROUP BY subscription_plan, onboarding_completed
ORDER BY total_segment_net_revenue DESC, churn_rate_pct DESC;
