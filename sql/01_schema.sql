-- =====================================================================
-- AstroGuide AI - Relational Database Schema (SQLite3 DDL)
-- File: sql/01_schema.sql
-- Description: Creates relational tables, constraints, foreign keys,
--              and performance indexes for customer churn analytics.
-- =====================================================================

-- Enforce Foreign Key Constraints in SQLite
PRAGMA foreign_keys = ON;

-- 1. Users Table (Dimension / Parent Entity)
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    signup_date DATE NOT NULL,
    acquisition_channel TEXT NOT NULL,
    country TEXT NOT NULL,
    age_group TEXT NOT NULL,
    device_type TEXT NOT NULL,
    marketing_campaign TEXT NOT NULL,
    onboarding_completed BOOLEAN NOT NULL,
    zodiac_sign TEXT NOT NULL,
    subscription_plan TEXT NOT NULL
);

-- 2. Subscriptions Table (Lifecycle Dimension/Fact)
DROP TABLE IF EXISTS subscriptions;
CREATE TABLE subscriptions (
    subscription_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    plan_name TEXT NOT NULL,
    subscription_start_date DATE NOT NULL,
    subscription_end_date DATE,
    billing_interval TEXT NOT NULL,
    subscription_status TEXT NOT NULL,
    renewal_count INTEGER NOT NULL,
    cancellation_date DATE,
    cancellation_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- 3. Transactions Table (Financial Fact Ledger)
DROP TABLE IF EXISTS transactions;
CREATE TABLE transactions (
    transaction_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    transaction_date DATE NOT NULL,
    product_type TEXT NOT NULL,
    amount REAL NOT NULL,
    currency TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    refund_flag BOOLEAN NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- 4. User Activity Table (Telemetry Event Stream)
DROP TABLE IF EXISTS user_activity;
CREATE TABLE user_activity (
    event_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    event_timestamp TEXT NOT NULL,
    event_date DATE NOT NULL,
    event_type TEXT NOT NULL,
    feature_name TEXT NOT NULL,
    session_duration_seconds INTEGER NOT NULL,
    notification_opened BOOLEAN NOT NULL,
    session_number INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- 5. Churn Labels Table (Target Classification Outcome)
DROP TABLE IF EXISTS churn_labels;
CREATE TABLE churn_labels (
    user_id TEXT PRIMARY KEY,
    observation_cutoff_date DATE NOT NULL,
    outcome_window_days INTEGER NOT NULL,
    outcome_sessions_count INTEGER NOT NULL,
    churn_label INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
);

-- =====================================================================
-- PERFORMANCE INDEXES
-- Optimize joins and filtering for analytics and cohort queries
-- =====================================================================
CREATE INDEX IF NOT EXISTS idx_users_signup_date ON users (signup_date);
CREATE INDEX IF NOT EXISTS idx_users_channel ON users (acquisition_channel);
CREATE INDEX IF NOT EXISTS idx_users_plan ON users (subscription_plan);

CREATE INDEX IF NOT EXISTS idx_subs_user_id ON subscriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_subs_status ON subscriptions (subscription_status);

CREATE INDEX IF NOT EXISTS idx_txns_user_id ON transactions (user_id);
CREATE INDEX IF NOT EXISTS idx_txns_date ON transactions (transaction_date);
CREATE INDEX IF NOT EXISTS idx_txns_status ON transactions (payment_status);

CREATE INDEX IF NOT EXISTS idx_activity_user_id ON user_activity (user_id);
CREATE INDEX IF NOT EXISTS idx_activity_date ON user_activity (event_date);
CREATE INDEX IF NOT EXISTS idx_activity_feature ON user_activity (feature_name);

CREATE INDEX IF NOT EXISTS idx_churn_label ON churn_labels (churn_label);
