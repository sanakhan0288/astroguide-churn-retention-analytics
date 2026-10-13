# AstroGuide AI — 3-Page Power BI Dashboard Specification & Assembly Guide

This document provides the exact visual layout specifications, canvas dimensions, color theme JSON, and step-by-step instructions for assembling the 3-page interactive report in **Power BI Desktop** on your Windows PC.

---

## 1. Visual Theme & Palette Configuration

In Power BI Desktop, go to **View** -> **Themes** -> **Customize current theme** (or import the JSON theme below):

```json
{
  "name": "AstroGuideExecutive",
  "dataColors": [
    "#3B82F6",
    "#10B981",
    "#EF4444",
    "#F59E0B",
    "#6366F1",
    "#8B5CF6",
    "#EC4899",
    "#64748B"
  ],
  "background": "#F1F5F9",
  "foreground": "#0F172A",
  "tableAccent": "#1E293B"
}
```

* **Canvas Setup:** 16:9 Widescreen (`1280 x 720` px)
* **Background:** Canvas background color set to `#F1F5F9` (10% transparency).

---

## 2. Page 1: Executive Overview

### Header & Slicers
* **Header Banner:** Shape / Text Box across top (`X: 0, Y: 0, W: 1280, H: 50`), Background `#1E293B`, Title: **ASTROGUIDE AI | EXECUTIVE OVERVIEW & RETENTION COHORTS** (White text, 14pt, Bold).
* **Slicer Pane (Top Right or Left Ribbon):**
  1. `DimDate[date]` (Between date range slider)
  2. `DimPlan[plan_name]` (Dropdown slicer)
  3. `DimUser[acquisition_channel]` (Dropdown slicer)
  4. `DimUser[device_type]` (Dropdown slicer)

### Top KPI Cards (`Y: 65, H: 90`)
| Position | Visual Type | Title / Measure | Display Value | Target Format | Subtitle / Callout |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Card 1** (`X: 30, W: 280`) | Card | `[Total Users]` | `10,000` | Whole Number | 7-Month Acquisition Cohort |
| **Card 2** (`X: 340, W: 280`) | Card | `[Net Realized Revenue]` | `$192,164` | Currency ($) | Gross: $194.4k \| Refunds: $2.2k |
| **Card 3** (`X: 650, W: 280`) | Card | `[Churn Rate]` | `42.98%` | Percentage | 4,298 Inactive Customers |
| **Card 4** (`X: 960, W: 280`) | Card | `[Paying Users Count]` | `5,745` | Whole Number | ARPPU: $33.45 \| Blended: $19.22 |

### Middle Visuals (`Y: 175, H: 250`)
1. **Visual 1: Monthly Realized Revenue Trend (`X: 30, W: 590`)**
   * **Visual Type:** Clustered Column & Line Chart (or Clustered Column Chart).
   * **X-Axis:** `DimDate[month_year]` (Sorted by `year_month_sort`).
   * **Y-Axis:** `_Measures[Net Realized Revenue]`.
   * **Line Y-Axis:** `_Measures[Churn Rate]`.
   * **Data Labels:** On.
   * **Title:** *Monthly Realized Revenue & Churn Rate Velocity*.

2. **Visual 2: Churn Rate by Acquisition Channel (`X: 650, W: 590`)**
   * **Visual Type:** Clustered Bar Chart (Horizontal).
   * **Y-Axis:** `DimUser[acquisition_channel]`.
   * **X-Axis:** `_Measures[Churn Rate]`.
   * **Conditional Formatting (Bars):** Rules -> If Value $< 0.40$ then `#10B981` (Green), else `#EF4444` (Red).
   * **Title:** *Customer Churn Rate by Acquisition Channel (%)*.

### Bottom Visuals (`Y: 445, H: 250`)
1. **Visual 3: Churn Rate by Subscription Plan Tier (`X: 30, W: 590`)**
   * **Visual Type:** Clustered Column Chart.
   * **X-Axis:** `DimPlan[plan_name]`.
   * **Y-Axis:** `_Measures[Churn Rate]`.
   * **Tooltip:** `_Measures[Total Users]`, `_Measures[Net Realized Revenue]`.
   * **Title:** *Churn Rate by Initial Subscription Plan Tier (%)*.

2. **Visual 4: Executive Key Takeaways Callout Card (`X: 650, W: 590`)**
   * **Visual Type:** Card / Multi-row card or Text box with white background card.
   * **Content:**
     * Annual Subscribers retain best (30.98% churn, 69.02% retention).
     * Weekly Subscribers experience severe turnover (52.16% churn) from renewal friction.
     * Social channels (TikTok: 45.5%, IG: 44.7%) require immediate onboarding optimization.
     * Organic & Referral deliver highest organic customer LTV ($33+ ARPPU).

---

## 3. Page 2: Engagement & Retention Diagnostics

### Header & Slicers
* **Title:** **ASTROGUIDE AI | PRODUCT TELEMETRY & RETENTION DIAGNOSTICS**

### Top KPI Cards (`Y: 65, H: 90`)
| Position | Visual Type | Measure | Display Value | Callout |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | Card | `[Onboarding Completion Rate]` | `69.07%` | 6,907 Activated Users |
| **Card 2** | Card | *Custom text* | `32.0% vs 67.4%` | 2.1x Higher Risk on Drop-off |
| **Card 3** | Card | `[Total Telemetry Events]` | `1,345,770` | Avg 134.6 Events / User |
| **Card 4** | Card | `[Average Session Duration (Minutes)]` | `1.68 min` | Avg 101 Seconds / Event |

### Visuals
1. **Visual 1: Onboarding Impact on Churn (`X: 30, W: 590, Y: 175, H: 250`)**
   * **Visual Type:** Clustered Column Chart.
   * **X-Axis:** `DimUser[onboarding_completed]`.
   * **Y-Axis:** `_Measures[Churn Rate]`.
   * **Title:** *Onboarding Completion vs. Churn Rate (%)*.

2. **Visual 2: Feature Telemetry Volume (`X: 650, W: 590, Y: 175, H: 250`)**
   * **Visual Type:** Clustered Bar Chart (Horizontal).
   * **Y-Axis:** `FactActivity[feature_name]`.
   * **X-Axis:** `_Measures[Total Telemetry Events]`.
   * **Data Labels:** Value & Percentage share.
   * **Title:** *Feature Telemetry Interaction Volume (Total Events)*.

3. **Visual 3: 30-Day Pre-Cutoff Inactivity Decay Curve (`X: 30, W: 590, Y: 445, H: 250`)**
   * **Visual Type:** Line Chart.
   * **X-Axis:** `Countdown Days (30 -> 0)`.
   * **Y-Axis:** `Average Events Per User`.
   * **Legend:** `Retained Cohort` vs `Churned Cohort`.
   * **Annotation:** Flags the critical **15-Day Warning Cliff**.

4. **Visual 4: Monthly Signup Cohort Retention Triangle (`X: 650, W: 590, Y: 445, H: 250`)**
   * **Visual Type:** Matrix Visual.
   * **Rows:** `DimUser[signup_month]` (2025-01 through 2025-07).
   * **Columns:** `Month Offset (M0, M1, M2, M3, M4, M5, M6)`.
   * **Values:** `[Active Users %]`.
   * **Conditional Formatting:** Background color gradient (Dark Green = 90%+, Pale Red = 50%).

---

## 4. Page 3: Churn Risk & Predictive Actions

### Header & Slicers
* **Title:** **ASTROGUIDE AI | PREDICTIVE CHURN RISK & LIFECYCLE INTERVENTIONS**

### Top KPI Cards (`Y: 65, H: 90`)
| Position | Visual Type | Measure | Display Value | Callout |
| :--- | :--- | :--- | :--- | :--- |
| **Card 1** | Card | `[At-Risk Users (High Risk)]` | `3,520` | 35.20% of Cohort |
| **Card 2** | Card | `[At-Risk Net Revenue]` | `$58,515` | 30.4% Revenue Exposure |
| **Card 3** | Card | *Callout* | `0.9294` | Model ROC-AUC Score |
| **Card 4** | Card | *Callout* | `15 Days` | Active Warning Window |

### Visuals
1. **Visual 1: Predicted Customer Risk Segmentation (`X: 30, W: 590, Y: 175, H: 250`)**
   * **Visual Type:** Donut Chart.
   * **Legend:** `FactChurnPrediction[risk_tier]`.
   * **Values:** `[Total Users]`.
   * **Colors:** Low Risk = `#10B981`, Medium Risk = `#F59E0B`, High Risk = `#EF4444`.
   * **Title:** *Customer Base by Churn Risk Tier*.

2. **Visual 2: At-Risk Net Revenue Exposure by Plan (`X: 650, W: 590, Y: 175, H: 250`)**
   * **Visual Type:** Clustered Column Chart.
   * **X-Axis:** `DimPlan[plan_name]`.
   * **Y-Axis:** `_Measures[At-Risk Net Revenue]`.
   * **Data Labels:** On ($ in Thousands).
   * **Title:** *At-Risk Net Revenue Exposure by Subscription Plan ($k)*.

3. **Visual 3: Recency vs. Churn Probability Scatter (`X: 30, W: 590, Y: 445, H: 250`)**
   * **Visual Type:** Scatter Chart.
   * **X-Axis:** `FactChurnPrediction[days_since_last_session]`.
   * **Y-Axis:** `FactChurnPrediction[churn_probability]`.
   * **Legend:** `FactChurnPrediction[risk_tier]`.
   * **Constant Line:** Y = 0.70 (High Risk Threshold).

4. **Visual 4: Actionable CRM Retention Campaigns Table (`X: 650, W: 590, Y: 445, H: 250`)**
   * **Visual Type:** Table Visual or Structured Callout.
   * **Recommended Campaigns:**
     1. *Weekly Subscribers:* Offer 20% discount coupon to upgrade to Monthly plan.
     2. *Onboarding Drop-offs:* Trigger automated push notification on Day 2: "Complete your birth chart for today's forecast".
     3. *Inactivity Gap $\ge$ 7 Days:* Re-engagement push highlighting major planetary transits.
     4. *Single-Feature Users:* Grant 1 Free AI Astrology Chat session upon next app open.
     5. *Annual Subscribers:* Exclusive VIP annual transit forecast and loyalty badges.
