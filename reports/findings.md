# AstroGuide AI — Executive Findings, Business Recommendations & A/B Testing Hypotheses

This comprehensive analytical report translates our exploratory findings, relational SQL cohort diagnostics, and predictive machine learning models into practical, testable retention strategies for the AstroGuide AI leadership team.

---

## 1. Executive Summary & Diagnostic Benchmarks

Across our cohort of **10,000 synthetic users** ($t_0 = \text{2025-08-31}$):

* **Baseline 30-Day Churn Rate:** **42.98%** (4,298 churned customers vs. 5,702 retained).
* **Net Realized Revenue:** **$192,163.62** across 27,562 transactions ($33.45 ARPPU).
* **At-Risk Revenue Exposure:** **$58,514.91** (30.4% of total net revenue) is concentrated among **3,520 users** flagged by our predictive model in the High Risk tier ($\ge 70\%$ churn probability).
* **The 15-Day Critical Opportunity Window:** Pre-churn telemetry demonstrates that churning users begin a precipitous engagement decline **15 to 20 days prior to churn**, falling from ~1.2 events/day to < 0.2 events/day in their final 5 days. This provides our lifecycle marketing team with an actionable window for automated re-engagement.

---

## 2. Empirical Findings Across Business Dimensions

### Finding 1: Onboarding Completion is the Primary Activation Anchor
* Users completing onboarding exhibit a **32.03% churn rate**.
* Users dropping out of onboarding exhibit a **67.44% churn rate**.
* **Analytical Reality:** Non-onboarded users experience a **2.1x churn risk multiplier**. Onboarding drop-off is the single largest behavioral differentiator of future user churn.

### Finding 2: Weekly Subscriptions Suffer Severe Renewal Friction
* **Annual Premium:** 30.98% churn rate (Lowest churn, $62.74 ARPU).
* **Monthly Premium:** 40.66% churn rate ($38.15 ARPU).
* **Weekly Premium:** 52.16% churn rate ($35.82 ARPU).
* **Analytical Reality:** Weekly micro-transactions ($3.99/week) generate repeated friction and cognitive cancellation triggers. Subscribers encounter 4 renewal notifications per month compared to 1 for monthly subscribers, driving premature fatigue.

### Finding 3: Paid Social Channels Bring Volume, but Suffer Activation Drop-Off
* **Referral & Organic Search:** Churn rates of **39.05%** and **39.46%** (high organic intent).
* **TikTok Ads & Instagram Ads:** Churn rates of **45.51%** and **44.68%**.
* **Analytical Reality:** While paid social campaigns drive strong top-of-funnel registration volume, they exhibit lower initial onboarding completion and faster drop-off.

### Finding 4: Multi-Feature Adoption Deters Churn
* Adopters of **AI Chat** and **Compatibility Reports** have churn rates of **38.74%** and **38.64%**, compared to **42.84%** for users who exclusively check daily horoscopes.

---

## 3. Actionable Retention Hypotheses & A/B Testing Framework

> [!IMPORTANT]
> **Methodological Guardrail:** Observational correlations do not constitute causal proof. We do not claim that any single feature or message will automatically prevent churn. All proposed initiatives must be framed as testable business hypotheses and evaluated via controlled A/B experiments.

---

### Hypothesis 1: Streamlining and Incentivizing First-Run Onboarding

| Parameter | Specification |
| :--- | :--- |
| **Target Segment** | New signups who fail to complete birth-chart setup within their first session (~30.9% of registrations). |
| **Empirical Evidence** | Non-onboarded users churn at **67.44%** (2.1x higher than the 32.03% churn of activated users). |
| **Proposed Intervention** | 1. Redesign onboarding into a 2-step progressive disclosure flow (Birth Date + Time only; city lookup optional).<br>2. Trigger an automated push notification at $H+24$: *"Your personal astrological birth chart is 50% complete — finish now to reveal your Rising Sign and today's planetary transit."* |
| **Primary Success Metric (KPI)**| **Onboarding Completion Rate** (Target: Increase from 69.1% to 78.0%).<br>**Secondary Metric:** Day-30 Retention Rate. |
| **Potential Downside / Cost** | Engineering effort to rebuild onboarding UI; slight risk of notification fatigue if push is sent too aggressively. |
| **A/B Experiment Design** | **Sample:** 100% of newly registered users over a 3-week test window.<br>**Variant A (Control - 50%):** Existing 5-step onboarding flow.<br>**Variant B (Treatment - 50%):** 2-step simplified wizard + $H+24$ push trigger.<br>**Statistical Power:** Minimum sample of 2,000 users per arm ($\alpha = 0.05, \beta = 0.80$). |

---

### Hypothesis 2: Weekly Subscription Migration to Monthly Tiers

| Parameter | Specification |
| :--- | :--- |
| **Target Segment** | Weekly Premium subscribers reaching their 2nd successful renewal cycle (1,877 users; $17.5k in at-risk revenue). |
| **Empirical Evidence** | Weekly subscribers suffer the highest churn across all paid tiers (**52.16%**), driven by frequent micro-billing fatigue. |
| **Proposed Intervention** | In-app upgrade prompt delivered 24 hours prior to renewal #3: *"Upgrade to Monthly for $7.99/mo (Save 50% compared to weekly) and unlock unlimited tarot readings."* |
| **Primary Success Metric (KPI)**| **Weekly-to-Monthly Plan Upgrade Rate** (Target: $\ge 15\%$ conversion).<br>**Secondary Metric:** 90-Day Cumulative Net Revenue per User. |
| **Potential Downside / Cost** | Short-term nominal discount on monthly subscription price ($7.99 vs. $9.99). However, modeled LTV increases significantly if monthly subscriber retention holds at 59.3%. |
| **A/B Experiment Design** | **Sample:** Active Weekly subscribers at Renewal #2.<br>**Variant A (Control - 50%):** Standard weekly billing continuation.<br>**Variant B (Treatment - 50%):** 20% discounted monthly migration incentive. |

---

### Hypothesis 3: Automated Inactivity Re-Engagement at Day 7 (The Warning Cliff)

| Parameter | Specification |
| :--- | :--- |
| **Target Segment** | Users exhibiting an active inactivity gap of $\ge 7$ consecutive days without an app open. |
| **Empirical Evidence** | Telemetry decay analysis proved that churned users begin dropping sharply **15 to 20 days prior to churn**, and average inter-session gaps jump from 3.0 days (retained) to 9.5 days (churned). |
| **Proposed Intervention** | Trigger a personalized celestial transit push notification precisely on Day 7 of inactivity: *"Major cosmic shift: Mars enters Scorpio today. Here is what it means for your [Zodiac Sign] career house."* |
| **Primary Success Metric (KPI)**| **48-Hour Re-Engagement Rate** (Target: $\ge 22\%$ of dormant users opening app).<br>**Secondary Metric:** Forward 30-Day Churn Rate. |
| **Potential Downside / Cost** | Push notifications may trigger uninstalls among completely disengaged users (monitor opt-out and app deletion rates closely). |
| **A/B Experiment Design** | **Sample:** Users reaching 7 consecutive days of inactivity.<br>**Variant A (Control - 50%):** Standard generic marketing digest.<br>**Variant B (Treatment - 50%):** Real-time personalized astrological transit hook. |

---

### Hypothesis 4: Cross-Feature Discovery for Single-Feature Users

| Parameter | Specification |
| :--- | :--- |
| **Target Segment** | Users whose telemetry indicates single-feature dependency (users who exclusively view daily horoscopes). |
| **Empirical Evidence** | Multi-feature users who adopt AI Chat and Compatibility Reports exhibit significantly lower churn (**38.6% - 38.7%**) compared to horoscope-only users (**42.8%**). |
| **Proposed Intervention** | Contextual banner at the conclusion of the daily horoscope reading: *"Curious how today's planetary transit impacts your love life? Ask AstroGuide AI 3 free interactive questions."* |
| **Primary Success Metric (KPI)**| **AI Chat Adoption Rate** (Target: $\ge 20\%$ trial adoption).<br>**Secondary Metric:** Average Session Duration (Minutes). |
| **Potential Downside / Cost** | LLM API token inference costs for free chat sessions. Requires hard rate-limiting (e.g., maximum 3 free questions per user per day). |
| **A/B Experiment Design** | **Sample:** Daily horoscope viewers with zero prior AI chat sessions.<br>**Variant A (Control):** Standard horoscope end-card.<br>**Variant B (Treatment):** 3-question free AI Chat prompt. |

---

### Hypothesis 5: VIP Loyalty Perks & Renewal Safeguards for Annual Subscribers

| Parameter | Specification |
| :--- | :--- |
| **Target Segment** | Annual Premium subscribers (594 users; highest baseline commitment and LTV at $62.74 ARPU). |
| **Empirical Evidence** | Annual subscribers represent our most loyal customer foundation (30.98% churn, 69.02% retention), but represent large lump-sum revenue renewals. |
| **Proposed Intervention** | Deliver an exclusive "Yearly Solar Return & Planetary Transit Dossier" 30 days prior to annual renewal, accompanied by an exclusive "Cosmic Founder" profile badge. |
| **Primary Success Metric (KPI)**| **Year 1 Annual Renewal Rate** (Target: Increase from 69.0% to 75.0%). |
| **Potential Downside / Cost** | Content generation and report templating overhead. |
| **Evaluation Method** | Cohort renewal tracking compared against baseline historical renewal benchmarks. |

---

## 4. Prioritization Matrix & Implementation Roadmap

```
IMPACT vs. EFFORT PRIORITIZATION:

High Impact  │  [Hypothesis 1: Onboarding Wizard]    [Hypothesis 2: Weekly Migration]
             │  * Urgent - 2.1x Risk Multiplier     * $17.5k At-Risk Revenue Exposure
             │
             │  [Hypothesis 3: Day-7 Inactivity Hook] [Hypothesis 4: AI Chat Discovery]
             │  * Capitalizes on 15d Cliff           * LLM Token Cost Managed
             │
Low Impact   │                                       [Hypothesis 5: Annual VIP Perks]
             └────────────────────────────────────────────────────────────────────────
               Low Effort                              High Effort
```

* **Sprint 1 (Weeks 1–2):** Deploy Hypothesis 1 (Onboarding A/B Test) and Hypothesis 3 (Day-7 Automated Push Trigger).
* **Sprint 2 (Weeks 3–4):** Implement Hypothesis 2 (Weekly-to-Monthly In-App Upgrade Incentive).
* **Sprint 3 (Weeks 5–6):** Roll out Hypothesis 4 (Cross-Feature Discovery for AI Chat).
