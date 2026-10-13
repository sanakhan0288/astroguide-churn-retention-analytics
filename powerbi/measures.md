# AstroGuide AI — Complete DAX Measures & Power Query Repository

This document serves as the complete, copy-paste ready reference for all **DAX Measures** and **Power Query transformations** required for the AstroGuide AI Power BI reporting suite.

---

## 1. Core Technical Concepts: Calculated Columns vs. DAX Measures

| Feature | Calculated Column | DAX Measure |
| :--- | :--- | :--- |
| **Evaluation Context** | **Row Context**: Evaluated row-by-row during data refresh. | **Filter Context**: Evaluated dynamically at query time based on user slicers and visual filters. |
| **RAM Storage** | Stored in memory (VertiPaq column-store RAM). Increases `.pbix` file size. | Takes **zero RAM storage**. Computed entirely in CPU on-the-fly. |
| **When to Use** | To create categorical slicers, row labels, or grouping buckets (e.g. `Tenure Bucket`, `Age Group`). | For all numerical calculations, ratios, aggregations, percentages, and financial KPIs. |

---

## 2. Best Practice: Dedicated DAX Measures Table (`_Measures`)

In Power BI, create an empty table dedicated exclusively to storing measures so they are neatly organized at the top of your field list:

1. Click **Home** -> **Enter Data**.
2. Name the table **`_Measures`** -> Click **Load**.
3. Create your measures inside this table.
4. Delete the default blank `Column1` from `_Measures`.
5. Notice that `_Measures` moves to the top of your field pane with a special calculator icon.

---

## 3. Complete DAX Measures Repository

### Category A: User Volume & Retention Metrics

#### 1. `[Total Users]`
* **Business Definition:** Total registered customer count across all acquisition cohorts.
* **DAX Formula:**
```dax
Total Users = 
DISTINCTCOUNT(DimUser[user_id])
```
* **Expected Value:** `10,000`

---

#### 2. `[Total Evaluated Users]`
* **Business Definition:** Count of users eligible for 30-day post-cutoff churn evaluation.
* **DAX Formula:**
```dax
Total Evaluated Users = 
CALCULATE(
    DISTINCTCOUNT(FactChurnPrediction[user_id]),
    NOT(ISBLANK(FactChurnPrediction[churn_label]))
)
```
* **Expected Value:** `10,000`

---

#### 3. `[Churned Users]`
* **Business Definition:** Users who recorded zero sessions during the 30-day evaluation window ($t_0$ to $t_0+30$).
* **DAX Formula:**
```dax
Churned Users = 
CALCULATE(
    DISTINCTCOUNT(FactChurnPrediction[user_id]),
    FactChurnPrediction[churn_label] = 1
)
```
* **Expected Value:** `4,298`

---

#### 4. `[Retained Users]`
* **Business Definition:** Users who recorded at least one active session during the 30-day evaluation window.
* **DAX Formula:**
```dax
Retained Users = 
CALCULATE(
    DISTINCTCOUNT(FactChurnPrediction[user_id]),
    FactChurnPrediction[churn_label] = 0
)
```
* **Expected Value:** `5,702`

---

#### 5. `[Churn Rate]`
* **Business Definition:** Percentage of evaluated users who churned.
* **DAX Formula:**
```dax
Churn Rate = 
DIVIDE(
    [Churned Users],
    [Total Evaluated Users],
    0
)
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `42.98%`

---

#### 6. `[Retention Rate]`
* **Business Definition:** Percentage of evaluated users who remained active.
* **DAX Formula:**
```dax
Retention Rate = 
DIVIDE(
    [Retained Users],
    [Total Evaluated Users],
    0
)
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `57.02%`

---

#### 7. `[Onboarding Completion Rate]`
* **Business Definition:** Proportion of users who completed initial birth-chart onboarding.
* **DAX Formula:**
```dax
Onboarding Completion Rate = 
DIVIDE(
    CALCULATE(COUNTROWS(DimUser), DimUser[onboarding_completed] = "Completed"),
    [Total Users],
    0
)
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `69.07%`

---

### Category B: Monetization & Revenue Metrics

#### 8. `[Gross Revenue]`
* **Business Definition:** Sum of all successful financial transactions, excluding failed settlement attempts.
* **DAX Formula:**
```dax
Gross Revenue = 
CALCULATE(
    SUM(FactTransactions[amount]),
    FactTransactions[payment_status] = "Success"
)
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$194,392.89`

---

#### 9. `[Total Refunds]`
* **Business Definition:** Total dollar volume of reversed or refunded transactions.
* **DAX Formula:**
```dax
Total Refunds = 
CALCULATE(
    SUM(FactTransactions[amount]),
    FactTransactions[refund_flag] = 1
)
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$2,229.27`

---

#### 10. `[Net Realized Revenue]`
* **Business Definition:** Realized net dollar revenue after accounting for refunded charges.
* **DAX Formula:**
```dax
Net Realized Revenue = 
[Gross Revenue] - [Total Refunds]
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$192,163.62`

---

#### 11. `[Paying Users Count]`
* **Business Definition:** Distinct count of unique customers who completed at least one successful transaction.
* **DAX Formula:**
```dax
Paying Users Count = 
CALCULATE(
    DISTINCTCOUNT(FactTransactions[user_id]),
    FactTransactions[payment_status] = "Success"
)
```
* **Expected Value:** `5,745`

---

#### 12. `[Average Revenue Per Paying User (ARPPU)]`
* **Business Definition:** Net revenue generated divided by the paying customer base.
* **DAX Formula:**
```dax
ARPPU = 
DIVIDE(
    [Net Realized Revenue],
    [Paying Users Count],
    0
)
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$33.45`

---

#### 13. `[Blended ARPU]`
* **Business Definition:** Net revenue divided across the entire acquired user base (free + paid).
* **DAX Formula:**
```dax
Blended ARPU = 
DIVIDE(
    [Net Realized Revenue],
    [Total Users],
    0
)
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$19.22`

---

#### 14. `[Premium Subscriber Share]`
* **Business Definition:** Percentage of users who enrolled in a paid subscription plan upon signup.
* **DAX Formula:**
```dax
Premium Subscriber Share = 
DIVIDE(
    CALCULATE(DISTINCTCOUNT(DimUser[user_id]), DimUser[initial_plan] <> "Free"),
    [Total Users],
    0
)
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `40.13%`

---

### Category C: Telemetry & Engagement Metrics

#### 15. `[Total Telemetry Events]`
* **Business Definition:** Total in-app event interactions recorded in telemetry logs.
* **DAX Formula:**
```dax
Total Telemetry Events = 
COUNTROWS(FactActivity)
```
* **Format:** `Whole Number (#,##0)` | **Expected Value:** `1,345,770`

---

#### 16. `[Average Session Duration (Minutes)]`
* **Business Definition:** Average duration of user interactions expressed in minutes.
* **DAX Formula:**
```dax
Average Session Duration (Minutes) = 
DIVIDE(
    AVERAGE(FactActivity[session_duration_seconds]),
    60,
    0
)
```
* **Format:** `Decimal Number (0.0)` | **Expected Value:** `1.68 min`

---

#### 17. `[Average Events Per User]`
* **Business Definition:** Total telemetry interactions divided by total users.
* **DAX Formula:**
```dax
Average Events Per User = 
DIVIDE(
    [Total Telemetry Events],
    [Total Users],
    0
)
```
* **Format:** `Decimal Number (0.0)` | **Expected Value:** `134.6`

---

### Category D: Predictive Churn Risk Measures (Model-Based)

#### 18. `[At-Risk Users (High Risk)]`
* **Business Definition:** Count of users flagged by the Logistic Regression model with $\ge 70\%$ predicted churn probability.
* **DAX Formula:**
```dax
At-Risk Users (High Risk) = 
CALCULATE(
    DISTINCTCOUNT(FactChurnPrediction[user_id]),
    FactChurnPrediction[risk_tier] = "High Risk (>=70%)"
)
```
* **Expected Value:** `3,520`

---

#### 19. `[High Risk Customer Share]`
* **Business Definition:** Proportion of customer base currently categorized in the High Risk tier.
* **DAX Formula:**
```dax
High Risk Customer Share = 
DIVIDE(
    [At-Risk Users (High Risk)],
    [Total Users],
    0
)
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `35.20%`

---

#### 20. `[Model Predicted Churn Rate]`
* **Business Definition:** Cohort-wide average of predicted churn probabilities generated by machine learning inference.
* **DAX Formula:**
```dax
Model Predicted Churn Rate = 
AVERAGE(FactChurnPrediction[churn_probability])
```
* **Format:** `Percentage (0.00%)` | **Expected Value:** `45.85%`

---

#### 21. `[At-Risk Net Revenue]`
* **Business Definition:** Net historical revenue associated with users currently in the High Risk tier.
* **DAX Formula:**
```dax
At-Risk Net Revenue = 
CALCULATE(
    [Net Realized Revenue],
    FILTER(
        FactChurnPrediction,
        FactChurnPrediction[risk_tier] = "High Risk (>=70%)"
    )
)
```
* **Format:** `Currency ($#,##0.00)` | **Expected Value:** `$58,514.91`

---

## 4. Power Query (M-Code) Best Practices & Recipes

When importing CSVs into Power BI Desktop, ensure the following Power Query transformations are applied:

### Recipe 1: Data Type Enforcement in `FactTransactions`
```powerquery
let
    Source = Csv.Document(File.Contents("C:\AstroGuide\data\processed\FactTransactions.csv"), [Delimiter=",", Columns=8, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"transaction_id", type text},
        {"user_id", type text},
        {"transaction_date", type date},
        {"product_type", type text},
        {"amount", Currency.Type},
        {"currency", type text},
        {"payment_status", type text},
        {"refund_flag", Int64.Type}
    })
in
    #"Changed Type"
```

### Recipe 2: Data Type Enforcement in `FactChurnPrediction`
```powerquery
let
    Source = Csv.Document(File.Contents("C:\AstroGuide\data\processed\FactChurnPrediction.csv"), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers",{
        {"user_id", type text},
        {"churn_label", Int64.Type},
        {"predicted_churn", Int64.Type},
        {"churn_probability", Percentage.Type},
        {"risk_tier", type text},
        {"tenure_days", Int64.Type},
        {"days_since_last_session", type number}
    })
in
    #"Changed Type"
```
