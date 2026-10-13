-- =====================================================================
-- AstroGuide AI - Cohort Retention & Advanced Window Functions
-- File: sql/04_retention_cohorts.sql
-- Description: Monthly signup cohort matrix, activity retention over time,
--              and advanced SQL window functions (ROW_NUMBER, LAG, LEAD, AVG OVER).
-- =====================================================================

-- ---------------------------------------------------------------------
-- QUERY 1: Monthly Signup Cohort Retention Matrix
-- Business Question: How do monthly registration cohorts retain over time?
-- Concepts: CTEs, strftime date formatting, multi-month cohort tracking,
--           conditional aggregation.
-- ---------------------------------------------------------------------
WITH user_cohorts AS (
    SELECT 
        user_id,
        signup_date,
        strftime('%Y-%m', signup_date) AS cohort_month
    FROM users
),
cohort_size AS (
    SELECT 
        cohort_month,
        COUNT(user_id) AS total_cohort_users
    FROM user_cohorts
    GROUP BY cohort_month
),
user_activity_months AS (
    SELECT DISTINCT
        ua.user_id,
        strftime('%Y-%m', ua.event_date) AS activity_month,
        (CAST(strftime('%Y', ua.event_date) AS INTEGER) - CAST(strftime('%Y', u.signup_date) AS INTEGER)) * 12 +
        (CAST(strftime('%m', ua.event_date) AS INTEGER) - CAST(strftime('%m', u.signup_date) AS INTEGER)) AS month_number
    FROM user_activity ua
    JOIN users u ON ua.user_id = u.user_id
    WHERE ua.event_date <= '2025-08-31'
),
cohort_retention AS (
    SELECT 
        uc.cohort_month,
        uam.month_number,
        COUNT(DISTINCT uam.user_id) AS active_users
    FROM user_cohorts uc
    INNER JOIN user_activity_months uam ON uc.user_id = uam.user_id
    GROUP BY uc.cohort_month, uam.month_number
)
SELECT 
    cr.cohort_month,
    cs.total_cohort_users,
    MAX(CASE WHEN cr.month_number = 0 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m0_retention_pct,
    MAX(CASE WHEN cr.month_number = 1 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m1_retention_pct,
    MAX(CASE WHEN cr.month_number = 2 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m2_retention_pct,
    MAX(CASE WHEN cr.month_number = 3 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m3_retention_pct,
    MAX(CASE WHEN cr.month_number = 4 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m4_retention_pct,
    MAX(CASE WHEN cr.month_number = 5 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m5_retention_pct,
    MAX(CASE WHEN cr.month_number = 6 THEN ROUND(cr.active_users * 100.0 / cs.total_cohort_users, 1) END) AS m6_retention_pct
FROM cohort_retention cr
INNER JOIN cohort_size cs ON cr.cohort_month = cs.cohort_month
GROUP BY cr.cohort_month, cs.total_cohort_users
ORDER BY cr.cohort_month ASC;


-- ---------------------------------------------------------------------
-- QUERY 2: User Session Sequence & Inactivity Gap Analysis
-- Business Purpose: Compute days elapsed between consecutive user sessions
--                   to detect engagement decay.
-- Concepts: WINDOW FUNCTIONS: LAG() OVER (PARTITION BY ... ORDER BY ...),
--           julianday date math, CTE.
-- ---------------------------------------------------------------------
WITH distinct_user_sessions AS (
    SELECT DISTINCT
        user_id,
        event_date
    FROM user_activity
    WHERE event_date <= '2025-08-31'
),
session_lags AS (
    SELECT 
        user_id,
        event_date,
        -- Previous session date for this user
        LAG(event_date, 1) OVER (
            PARTITION BY user_id 
            ORDER BY event_date ASC
        ) AS prev_event_date,
        -- Rank of the session for the user
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY event_date ASC
        ) AS session_rank
    FROM distinct_user_sessions
),
session_gaps AS (
    SELECT 
        user_id,
        event_date,
        prev_event_date,
        session_rank,
        ROUND(julianday(event_date) - julianday(prev_event_date)) AS days_since_last_session
    FROM session_lags
    WHERE prev_event_date IS NOT NULL
)
SELECT 
    CASE 
        WHEN c.churn_label = 1 THEN 'Churned Users' 
        ELSE 'Retained Users' 
    END AS customer_group,
    ROUND(AVG(sg.days_since_last_session), 2) AS avg_days_between_sessions,
    MAX(sg.days_since_last_session) AS max_days_inactivity_gap,
    COUNT(sg.user_id) AS total_inter_session_transitions
FROM session_gaps sg
INNER JOIN churn_labels c ON sg.user_id = c.user_id
GROUP BY c.churn_label;


-- ---------------------------------------------------------------------
-- QUERY 3: Cumulative User Telemetry & Running Total via Window Functions
-- Business Purpose: Calculate 7-day rolling average session activity per user.
-- Concepts: WINDOW FUNCTIONS: SUM() OVER, AVG() OVER with moving frame
--           (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW).
-- ---------------------------------------------------------------------
WITH daily_activity AS (
    SELECT 
        user_id,
        event_date,
        COUNT(event_id) AS events_count,
        SUM(session_duration_seconds) AS total_duration_seconds
    FROM user_activity
    WHERE event_date <= '2025-08-31'
    GROUP BY user_id, event_date
),
rolling_metrics AS (
    SELECT 
        user_id,
        event_date,
        events_count,
        -- Running cumulative total of events logged by this user
        SUM(events_count) OVER (
            PARTITION BY user_id 
            ORDER BY event_date ASC
        ) AS cumulative_events_to_date,
        -- 7-day moving average of daily duration
        ROUND(AVG(total_duration_seconds) OVER (
            PARTITION BY user_id 
            ORDER BY event_date ASC 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 1) AS rolling_7d_avg_duration_sec
    FROM daily_activity
)
SELECT 
    r.user_id,
    u.subscription_plan,
    r.event_date,
    r.events_count,
    r.cumulative_events_to_date,
    r.rolling_7d_avg_duration_sec
FROM rolling_metrics r
INNER JOIN users u ON r.user_id = u.user_id
WHERE r.user_id IN ('USR_000001', 'USR_000002', 'USR_000005')
ORDER BY r.user_id, r.event_date DESC
LIMIT 15;


-- ---------------------------------------------------------------------
-- QUERY 4: Lead/Lag Analysis of Subscription Cancellations
-- Business Purpose: Compare days between subscription signup and cancellation.
-- Concepts: DENSE_RANK() OVER, LEAD(), cancellation reason breakdown.
-- ---------------------------------------------------------------------
SELECT 
    plan_name,
    cancellation_reason,
    COUNT(subscription_id) AS cancellation_count,
    ROUND(AVG(renewal_count), 2) AS avg_renewals_before_cancel,
    ROUND(AVG(julianday(cancellation_date) - julianday(subscription_start_date)), 1) AS avg_lifetime_days_before_cancel,
    DENSE_RANK() OVER (ORDER BY COUNT(subscription_id) DESC) AS reason_frequency_rank
FROM subscriptions
WHERE subscription_status = 'Cancelled'
GROUP BY plan_name, cancellation_reason
ORDER BY cancellation_count DESC
LIMIT 10;
