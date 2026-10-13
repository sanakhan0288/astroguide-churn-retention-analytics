# Power BI Data Architecture & Dimensional Model

This directory contains the documentation, measure specifications, and visual guidelines for building the 3-page interactive Power BI dashboard for **AstroGuide AI**.

## Star Schema Architecture

* **Fact Tables:**
  * `FactActivity`: Granular user engagement and event telemetry.
  * `FactTransactions`: Revenue, subscription renewals, one-time charges, and refunds.
  * `FactChurnPrediction`: Model-generated risk probabilities and churn classifications.
* **Dimension Tables:**
  * `DimUser`: User demographics, acquisition channels, device types, onboarding status.
  * `DimPlan`: Subscription plans, pricing tiers, billing intervals.
  * `DimDate`: Dedicated calendar table with standard date hierarchies.

## Directory Contents

* `measures.md`: Complete repository of verified DAX formulas.
* `screenshots/`: Visual snapshots of each finished dashboard page.
