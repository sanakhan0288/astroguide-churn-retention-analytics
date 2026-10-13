# AstroGuide AI — Exploratory Data Analysis & Business Findings

This report documents the empirical findings from our customer churn and retention analysis across 10,000 synthetic users. All metrics are calculated strictly using pre-cutoff observation data ($t \le 2025-08-31$) with churn verified over the subsequent 30-day forward outcome window ($2025-09-01$ to $2025-09-30$).

---

## 1. Executive Summary & Churn Benchmarks

* **Total Active Cohort:** 10,000 users registered between Jan 1, 2025 and Jul 31, 2025.
* **Overall 30-Day Churn Rate:** **42.98%** (4,298 churned users vs. 5,702 retained users).
* **Net Realized Revenue:** **$192,163.62** across 27,562 ledger transactions.
* **Core Takeaway:** Churn is heavily concentrated among users who abandon the initial onboarding flow and weekly subscription members experiencing renewal fatigue.

---

## 2. Key Findings Across Business Dimensions

### A. Onboarding Completion is the Primary Retention Anchor
* **Completed Onboarding:** **32.03%** churn rate.
* **Dropped Off Onboarding:** **67.44%** churn rate.
* **Analytical Finding:** Users who fail to complete their birth-chart configuration during their first session churn at **2.1x the rate** of activated users. Onboarding drop-off is the single largest behavioral differentiator of future churn.

### B. Subscription Plan Retention & Lifetime Value
* **Annual Premium ($59.99/yr):** **30.98%** churn rate. Demonstrates highest customer lifetime value and commitment.
* **Monthly Premium ($9.99/mo):** **40.45%** churn rate. Healthy baseline retention with steady renewal cycles.
* **Weekly Premium ($3.99/wk):** **52.16%** churn rate. Exhibits highest churn among paid tiers. Frequent weekly micro-charges create recurring friction and cognitive cancellation triggers.
* **Free Tier:** **41.89%** churn rate.

### C. Acquisition Channel Quality
* **Referral & Organic Search:** Lowest churn rates (~36.8% and ~38.4%), driven by higher organic user intent.
* **TikTok Ads & Instagram Ads:** Higher churn rates (~46.2% and ~45.1%). While social campaigns bring high top-of-funnel installation volume, they exhibit lower initial activation and faster session drop-off.

### D. Feature Engagement Breakdown
* **Total Telemetry Events Logged:** 1,345,770 events.
* **Most Used Features:**
  1. *Daily Horoscope Views:* ~40% of all feature interactions (habit-forming daily hook).
  2. *AI Astrology Chat Sessions:* ~20% of interactions (highest session duration: avg 240 seconds).
  3. *Tarot Readings & Compatibility Reports:* ~30% combined (key drivers of one-off monetized purchases).
* **Behavioral Warning Signals:**
  * For churned users, session frequency begins a steep downward trajectory **15 to 20 days prior to the cutoff date**.
  * By day 5 prior to cutoff, churned users average fewer than 0.2 events/day compared to 1.4 events/day for retained users. This 15-day window represents our critical intervention window.

---

## 3. Financial Reconciliation

* **Gross Successful Billings:** $194,392.89
* **Refunded Transactions:** $2,229.27 (1.15% refund rate)
* **Net Realized Revenue:** $192,163.62
* **Failed Payments (Excluded from Revenue):** $3,164.22
* **Subscription Renewals vs. One-Off Products:**
  * Subscription charges represent ~78.5% of total revenue.
  * One-off premium reports (Compatibility Full Reports and Tarot Deep Dives) represent ~21.5% of gross revenue, providing an effective low-friction monetization pathway for non-subscribers.

---

## 4. Visual Assets Generated

The following analytical plots have been generated and saved to `reports/figures/`:
1. `reports/figures/churn_distribution.png`: Overall cohort breakdown.
2. `reports/figures/churn_by_channel.png`: Marketing channel comparison.
3. `reports/figures/churn_by_plan.png`: Subscription tier retention performance.
4. `reports/figures/onboarding_vs_churn.png`: Onboarding completion impact.
5. `reports/figures/feature_usage_distribution.png`: Event volume by application module.
6. `reports/figures/engagement_decay_pre_churn.png`: 30-day pre-churn telemetry decay curves.
7. `reports/figures/revenue_by_plan.png`: Realized revenue distribution.
8. `reports/figures/tenure_vs_churn.png`: Churn curves by user tenure cohorts.
