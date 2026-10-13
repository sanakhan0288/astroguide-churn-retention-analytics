-- =====================================================================
-- AstroGuide AI - Core Business & Revenue Analysis
-- File: sql/02_business_analysis.sql
-- Description: Core monetization metrics, ARPU, plan performance,
--              and acquisition channel revenue breakdown.
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Executive KPI Summary — Users, Paying Users & Realized Revenue
-- Business Purpose: High-level financial reconciliation dashboard metric.
-- Concepts: Aggregate functions (COUNT, SUM), CASE WHEN, conditional filtering.
-- ---------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT u.user_id) AS total_registered_users,
    COUNT(DISTINCT CASE WHEN t.payment_status = 'Success' THEN t.user_id END) AS total_paying_users,
    ROUND(COUNT(DISTINCT CASE WHEN t.payment_status = 'Success' THEN t.user_id END) * 100.0 / COUNT(DISTINCT u.user_id), 2) AS payer_conversion_rate_pct,
    ROUND(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END), 2) AS gross_revenue_usd,
    ROUND(SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END), 2) AS refunded_amount_usd,
    ROUND(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) - 
          SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END), 2) AS net_realized_revenue_usd,
    ROUND(SUM(CASE WHEN t.payment_status = 'Failed' THEN t.amount ELSE 0 END), 2) AS failed_payment_volume_usd
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id;


-- ---------------------------------------------------------------------
-- QUERY 2: Revenue & Average Revenue Per User (ARPU) by Acquisition Channel
-- Business Purpose: Identify which marketing channels bring the highest-value
--                   customers to optimize digital ad spend allocation.
-- Concepts: LEFT JOIN, GROUP BY, ORDER BY, ROUND, conditional aggregation.
-- ---------------------------------------------------------------------
SELECT 
    u.acquisition_channel,
    COUNT(DISTINCT u.user_id) AS total_users,
    COUNT(DISTINCT CASE WHEN t.payment_status = 'Success' THEN t.user_id END) AS paying_users,
    ROUND(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) - 
          SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END), 2) AS net_revenue_usd,
    -- Blended ARPU (Net Revenue / All Acquired Users)
    ROUND((SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) - 
           SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END)) / COUNT(DISTINCT u.user_id), 2) AS blended_arpu_usd,
    -- ARPPU (Net Revenue / Paying Users Only)
    ROUND((SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) - 
           SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END)) / 
           NULLIF(COUNT(DISTINCT CASE WHEN t.payment_status = 'Success' THEN t.user_id END), 0), 2) AS arppu_usd
FROM users u
LEFT JOIN transactions t ON u.user_id = t.user_id
GROUP BY u.acquisition_channel
ORDER BY net_revenue_usd DESC;


-- ---------------------------------------------------------------------
-- QUERY 3: Realized Revenue & Transaction Volume by Product Type
-- Business Purpose: Measure the revenue contribution of recurring subscriptions
--                   versus one-time micro-transactions (tarot readings, reports).
-- Concepts: INNER JOIN, GROUP BY, HAVING, subquery/window share calculation.
-- ---------------------------------------------------------------------
SELECT 
    t.product_type,
    COUNT(t.transaction_id) AS successful_transactions_count,
    ROUND(SUM(t.amount), 2) AS gross_revenue_usd,
    ROUND(AVG(t.amount), 2) AS avg_transaction_value_usd,
    ROUND(SUM(t.amount) * 100.0 / (SELECT SUM(amount) FROM transactions WHERE payment_status = 'Success'), 2) AS revenue_share_pct
FROM transactions t
WHERE t.payment_status = 'Success'
GROUP BY t.product_type
HAVING COUNT(t.transaction_id) > 100
ORDER BY gross_revenue_usd DESC;


-- ---------------------------------------------------------------------
-- QUERY 4: Monthly Recurring Revenue (MRR) Trend by Subscription Tier
-- Business Purpose: Track monthly top-line revenue velocity and product mix.
-- Concepts: strftime (date extraction), conditional aggregation, GROUP BY.
-- ---------------------------------------------------------------------
SELECT 
    strftime('%Y-%m', t.transaction_date) AS transaction_month,
    ROUND(SUM(CASE WHEN s.plan_name = 'Annual_Premium' AND t.payment_status = 'Success' THEN t.amount ELSE 0 END), 2) AS annual_plan_revenue,
    ROUND(SUM(CASE WHEN s.plan_name = 'Monthly_Premium' AND t.payment_status = 'Success' THEN t.amount ELSE 0 END), 2) AS monthly_plan_revenue,
    ROUND(SUM(CASE WHEN s.plan_name = 'Weekly_Premium' AND t.payment_status = 'Success' THEN t.amount ELSE 0 END), 2) AS weekly_plan_revenue,
    ROUND(SUM(CASE WHEN t.payment_status = 'Success' AND t.product_type NOT LIKE 'Subscription%' THEN t.amount ELSE 0 END), 2) AS one_off_purchases_revenue,
    ROUND(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END), 2) AS total_monthly_gross_revenue
FROM transactions t
LEFT JOIN subscriptions s ON t.user_id = s.user_id 
    AND t.product_type IN ('Subscription_Initial', 'Subscription_Renewal')
WHERE t.payment_status = 'Success'
GROUP BY strftime('%Y-%m', t.transaction_date)
ORDER BY transaction_month ASC;


-- ---------------------------------------------------------------------
-- QUERY 5: Customer Lifetime Value (LTV) Segmentation
-- Business Purpose: Segment customer base into monetization tiers
--                   (Whale, Medium, Low, Free) for personalized lifecycle marketing.
-- Concepts: CTE (Common Table Expression), CASE WHEN bucket creation, GROUP BY.
-- ---------------------------------------------------------------------
WITH user_spend AS (
    SELECT 
        u.user_id,
        u.acquisition_channel,
        COALESCE(SUM(CASE WHEN t.payment_status = 'Success' THEN t.amount ELSE 0 END) -
                 SUM(CASE WHEN t.refund_flag = 1 THEN t.amount ELSE 0 END), 0) AS net_spend
    FROM users u
    LEFT JOIN transactions t ON u.user_id = t.user_id
    GROUP BY u.user_id, u.acquisition_channel
)
SELECT 
    CASE 
        WHEN net_spend >= 50 THEN '1. High Value ($50+)'
        WHEN net_spend >= 20 THEN '2. Medium Value ($20-$49)'
        WHEN net_spend > 0   THEN '3. Low Value ($0.01-$19.99)'
        ELSE '4. Zero Spend (Free User)'
    END AS ltv_segment,
    COUNT(user_id) AS total_users,
    ROUND(COUNT(user_id) * 100.0 / (SELECT COUNT(*) FROM users), 2) AS user_share_pct,
    ROUND(SUM(net_spend), 2) AS segment_net_revenue,
    ROUND(SUM(net_spend) * 100.0 / (SELECT SUM(net_spend) FROM user_spend), 2) AS revenue_contribution_pct,
    ROUND(AVG(net_spend), 2) AS avg_spend_per_user
FROM user_spend
GROUP BY ltv_segment
ORDER BY ltv_segment ASC;
