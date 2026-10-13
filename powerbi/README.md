# Power BI Data Architecture & Star Schema Model

This documentation provides the complete dimensional data model blueprint for building the **AstroGuide AI Customer Churn & Retention Analytics** dashboard in Microsoft Power BI Desktop.

---

## 1. Dimensional Model Overview (Star Schema)

The analytical data layer is organized in an enterprise **Star Schema**, cleanly separating descriptive business dimensions from high-volume transaction and telemetry fact tables.

```mermaid
erDiagram
    DimUser ||--o{ FactActivity : "user_id (1 to many)"
    DimUser ||--o{ FactTransactions : "user_id (1 to many)"
    DimUser ||--|| FactChurnPrediction : "user_id (1 to 1)"
    DimPlan ||--o{ DimUser : "plan_name to initial_plan (1 to many)"
    DimDate ||--o{ FactActivity : "date to event_date (1 to many)"
    DimDate ||--o{ FactTransactions : "date to transaction_date (1 to many)"

    DimUser {
        string user_id PK
        date signup_date
        string acquisition_channel
        string country
        string age_group
        string device_type
        string marketing_campaign
        string onboarding_completed
        string zodiac_sign
        string initial_plan FK
    }

    DimPlan {
        string plan_name PK
        string billing_interval
        float price_usd
        int duration_days
        int tier_rank
    }

    DimDate {
        date date PK
        int year
        string quarter
        int month_num
        string month_name
        string month_year
        int day_of_month
        string day_name
        int is_weekend
        int year_month_sort
    }

    FactActivity {
        string event_id PK
        string user_id FK
        date event_date FK
        string event_type
        string feature_name
        int session_duration_seconds
        int notification_opened
        int session_number
    }

    FactTransactions {
        string transaction_id PK
        string user_id FK
        date transaction_date FK
        string product_type
        float amount
        string currency
        string payment_status
        int refund_flag
    }

    FactChurnPrediction {
        string user_id PK_FK
        int churn_label
        int predicted_churn
        float churn_probability
        string risk_tier
        int tenure_days
        float days_since_last_session
    }
```

---

## 2. Table Specifications & Roles

### Dimension Tables (Descriptive Context)

| Table Name | Source File | Primary Key | Description & Role |
| :--- | :--- | :--- | :--- |
| **`DimUser`** | `data/processed/DimUser.csv` | `user_id` | Core customer profile containing acquisition channel, demographics, onboarding status, and device metadata. |
| **`DimPlan`** | `data/processed/DimPlan.csv` | `plan_name` | Subscription tier master table containing price points, duration, and billing intervals (Free, Weekly, Monthly, Annual). |
| **`DimDate`** | `data/processed/DimDate.csv` | `date` | Contiguous calendar dimension covering Jan 1, 2025 through Sep 30, 2025. Required for Time Intelligence DAX functions. |

### Fact Tables (Numerical Metrics & Telemetry)

| Table Name | Source File | Primary Key | Foreign Keys | Description & Role |
| :--- | :--- | :--- | :--- | :--- |
| **`FactActivity`** | `data/processed/FactActivity.csv` | `event_id` | `user_id`, `event_date` | High-frequency telemetry event stream (1.35M rows) tracking horoscope views, AI chat sessions, tarot readings, and duration. |
| **`FactTransactions`** | `data/processed/FactTransactions.csv` | `transaction_id` | `user_id`, `transaction_date` | Financial transactions ledger capturing recurring renewals, one-time report sales, refunds, and failed payments. |
| **`FactChurnPrediction`** | `data/processed/fact_churn_prediction.csv` | `user_id` | `user_id` | Machine learning model inference table providing ground-truth churn labels, predicted churn probabilities, and assigned risk tiers. |

---

## 3. Relationships & Filter Propagation Rules

| From (Dimension) | To (Fact) | Cardinality | Cross-Filter Direction | Security / Performance Rationale |
| :--- | :--- | :--- | :--- | :--- |
| `DimUser[user_id]` | `FactActivity[user_id]` | **1 to Many (1:*)** | **Single (Dim -> Fact)** | Dimension filters activity. Prevents circular ambiguity. |
| `DimUser[user_id]` | `FactTransactions[user_id]` | **1 to Many (1:*)** | **Single (Dim -> Fact)** | Allows slicing revenue by user demographics and channels. |
| `DimUser[user_id]` | `FactChurnPrediction[user_id]` | **1 to 1 (1:1)** | **Single (Dim -> Fact)** | Maps risk probabilities and predictions directly to each user. |
| `DimPlan[plan_name]` | `DimUser[initial_plan]` | **1 to Many (1:*)** | **Single (Dim -> Fact)** | Enables plan-level filtering across all users and activities. |
| `DimDate[date]` | `FactActivity[event_date]` | **1 to Many (1:*)** | **Single (Dim -> Fact)** | Powers daily and weekly trend visual filtering. |
| `DimDate[date]` | `FactTransactions[transaction_date]` | **1 to Many (1:*)** | **Single (Dim -> Fact)** | Powers monthly recurring revenue (MRR) time intelligence. |

> [!IMPORTANT]
> **Why We Avoid Bi-Directional Cross-Filtering:**
> Setting relationships to "Both" (bi-directional) creates multiple active relationship paths, degrades VertiPaq engine query cache performance, and can produce unexpected Cartesian totals in DAX measures. All relationships in this model use **Single** filter direction.

---

## 4. The Critical Role of `DimDate` in Power BI

1. **Time Intelligence Functions**: DAX time intelligence functions (e.g. `TOTALYTD`, `SAMEPERIODLASTYEAR`, `DATESINPERIOD`, `DATEADD`) require an unbroken, contiguous date table. If dates have missing calendar days (e.g. days with no transactions), standard DAX time calculations return erroneous results.
2. **Eliminating "Auto Date/Time" Bloat**: By default, Power BI creates a hidden background date hierarchy table for every single date column in your dataset. Marking `DimDate` as an official Date Table allows you to disable Auto Date/Time (*File -> Options -> Current File -> Data Load -> uncheck Auto Date/Time*), reducing `.pbix` memory footprint by up to 40%.
3. **Sort-by-Column Configuration**:
   * Select `month_name` in the field list -> Click **Column Tools** -> **Sort by Column** -> Choose **`month_num`** (ensures months sort chronologically from January to September rather than alphabetically).
   * Select `month_year` -> Sort by **`year_month_sort`**.

---

## 5. Step-by-Step Data Import Guide (For Your Windows PC)

When opening **Power BI Desktop** on your Windows PC:

### Step 1: Copy Data Files
Copy the `data/processed/` folder from this repository to a folder on your Windows PC (e.g., `C:\AstroGuide\data\processed\`).

### Step 2: Ingest CSVs via Power Query
1. Open Power BI Desktop -> Click **Get Data** -> **Text/CSV**.
2. Select each file one by one:
   * `DimUser.csv`
   * `DimPlan.csv`
   * `DimDate.csv`
   * `FactTransactions.csv`
   * `FactChurnPrediction.csv`
   * `FactActivity.csv`
3. Click **Transform Data** to open the Power Query Editor.

### Step 3: Verify Column Data Types in Power Query
* **`DimDate`**: Ensure `date` is set to `Date`. Ensure `year`, `month_num`, `day_of_month` are set to `Whole Number`.
* **`FactTransactions`**: Ensure `amount` is set to `Fixed Decimal Number` (Currency) or `Decimal Number`. `refund_flag` set to `Whole Number`.
* **`FactChurnPrediction`**: Ensure `churn_probability` is set to `Decimal Number` (Percentage).
* Click **Close & Apply**.

### Step 4: Configure Relationships in Model View
1. Switch to the **Model View** (icon with 3 boxes on the left sidebar).
2. Drag and drop keys between tables as defined in Section 3 above:
   * `DimUser[user_id]` -> `FactTransactions[user_id]`
   * `DimUser[user_id]` -> `FactActivity[user_id]`
   * `DimUser[user_id]` -> `FactChurnPrediction[user_id]`
   * `DimDate[date]` -> `FactTransactions[transaction_date]`
   * `DimDate[date]` -> `FactActivity[event_date]`
   * `DimPlan[plan_name]` -> `DimUser[initial_plan]`
3. Right-click `DimDate` -> **Mark as date table** -> Select `date` column -> Click OK.
