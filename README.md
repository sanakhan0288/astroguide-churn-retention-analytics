# AstroGuide AI — Customer Churn Prediction & Retention Analytics

An end-to-end data analytics and machine learning portfolio project analyzing customer engagement, churn drivers, and revenue optimization for a fictional subscription-based astrology and horoscope application.

---

## 📌 Executive Summary & Scenario

**AstroGuide AI** is a mobile and web application providing AI-generated daily horoscopes, personalized birth chart readings, interactive astrology chat, and tarot-style readings. The business monetizes through tiered recurring subscriptions (Weekly, Monthly, Annual) and one-time premium reports.

### Key Business Questions
1. **Churn Measurement:** What proportion of users become inactive, and how quickly does churn occur across different plans?
2. **Behavioral Drivers:** How do onboarding completion, session frequency, and specific feature interactions relate to retention?
3. **Revenue Impact:** Which subscription tiers deliver the highest customer lifetime value (LTV) versus high churn risk?
4. **Predictive Retention:** Can we identify at-risk users before they churn without leaking future information?
5. **Business Action:** What retention campaigns (push notifications, re-engagement offers) should be prioritized and A/B tested?

> **Note on Data:** All datasets used in this project are synthetically generated for educational and portfolio demonstration purposes.

---

## 🛠️ Technology Stack

| Category | Tools & Libraries |
| :--- | :--- |
| **Programming & Data Processing** | Python 3.13, pandas, NumPy, pathlib |
| **Statistical Analysis & Visualization** | matplotlib, seaborn |
| **Machine Learning** | scikit-learn (Pipelines, Logistic Regression, Classification Metrics) |
| **Database & SQL** | SQLite3, Standard SQL (CTEs, Window Functions, Aggregations) |
| **Business Intelligence** | Microsoft Power BI (Star Schema, Power Query, DAX Measures) |
| **Testing & Quality** | pytest (automated validation & foreign-key integrity tests) |
| **Version Control & Environment** | Git, GitHub, Python `venv` |

---

## 📂 Repository Structure

```text
astroguide-churn-retention-analytics/
├── data/
│   ├── raw/                 # Generated synthetic raw CSV files
│   ├── processed/           # Transformed, cleaned, and star-schema analytical tables
│   └── README.md            # Data dictionary and schema specifications
├── notebooks/
│   ├── 01_data_quality_and_eda.ipynb      # Exploratory Data Analysis & visual insights
│   ├── 02_churn_and_retention_analysis.ipynb # Cohort & tenure analysis
│   └── 03_churn_prediction.ipynb          # Baseline & predictive modeling
├── src/
│   ├── generate_data.py     # Configurable synthetic data generator
│   ├── validate_data.py     # Automated data quality & integrity checks
│   ├── prepare_data.py      # Star-schema & feature table transformation
│   ├── load_database.py     # SQLite database loading script
│   ├── features.py          # Leakage-free feature engineering
│   └── train_model.py       # Scikit-learn model training & evaluation
├── sql/
│   ├── 01_schema.sql             # Table DDL, primary/foreign keys, and indexes
│   ├── 02_business_analysis.sql  # Core KPI aggregations & revenue breakdown
│   ├── 03_churn_analysis.sql     # Segmented churn & tenure queries
│   └── 04_retention_cohorts.sql  # Rolling cohort retention & window functions
├── powerbi/
│   ├── README.md            # Data model architecture & setup instructions
│   ├── measures.md          # Complete DAX formulas & measure documentation
│   └── screenshots/         # Dashboard visuals and page mockups
├── reports/
│   ├── figures/             # Exported visualizations and plots
│   └── findings.md          # Business insights & retention strategy report
├── tests/
│   ├── test_data_validation.py  # Automated tests for data integrity
│   └── test_features.py         # Tests preventing data leakage
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/sanakhan0288/astroguide-churn-retention-analytics.git
cd astroguide-churn-retention-analytics
```

### 2. Create and Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate    # On macOS/Linux
# .venv\Scripts\activate     # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 🗺️ Project Milestones

- [x] **Milestone 1:** Environment, Tooling & Project Architecture Setup
- [ ] **Milestone 2:** Synthetic Relational Dataset Generation & Validation Engine
- [ ] **Milestone 3:** Exploratory Data Analysis (EDA) & Business Insights
- [ ] **Milestone 4:** SQLite Relational Database & Advanced SQL Analysis
- [ ] **Milestone 5:** Leakage-Aware Machine Learning Churn Prediction
- [ ] **Milestone 6:** Power BI Dimensional Modeling & Star Schema
- [ ] **Milestone 7:** DAX Measures & Power Query Logic
- [ ] **Milestone 8:** 3-Page Executive Power BI Dashboard Build
- [ ] **Milestone 9:** Actionable Retention Strategies & Experimentation Hypotheses
- [ ] **Milestone 10:** End-to-End Testing & Reproducibility Pipeline
- [ ] **Milestone 11:** GitHub Version Control & Repository Review
- [ ] **Milestone 12:** Portfolio Documentation, Case Study & Interview Preparation
