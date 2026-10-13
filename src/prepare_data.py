"""
AstroGuide AI - Star Schema Dimensional Data Preparation
=========================================================
Transforms relational tables and model outputs into clean, standardized
Star Schema Dimension and Fact tables for Power BI Desktop.

Exports:
- data/processed/DimUser.csv
- data/processed/DimPlan.csv
- data/processed/DimDate.csv
- data/processed/FactActivity.csv
- data/processed/FactTransactions.csv
- data/processed/FactChurnPrediction.csv

Author: AstroGuide Analytics Team
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def generate_dim_date(start_date_str: str = "2025-01-01", end_date_str: str = "2025-09-30") -> pd.DataFrame:
    """
    Generate contiguous calendar dimension table with standard hierarchies.
    Essential for Power BI Time Intelligence DAX functions (YTD, MTD, SAMEPERIODLASTYEAR).
    """
    logger.info("Generating DimDate from %s to %s...", start_date_str, end_date_str)
    start_dt = pd.to_datetime(start_date_str)
    end_dt = pd.to_datetime(end_date_str)
    dates = pd.date_range(start_dt, end_dt, freq="D")

    dim_date = pd.DataFrame({"date": dates.strftime("%Y-%m-%d")})
    dt_series = pd.to_datetime(dim_date["date"])

    dim_date["year"] = dt_series.dt.year
    dim_date["quarter"] = "Q" + dt_series.dt.quarter.astype(str)
    dim_date["month_num"] = dt_series.dt.month
    dim_date["month_name"] = dt_series.dt.strftime("%B")
    dim_date["month_year"] = dt_series.dt.strftime("%b %Y")
    dim_date["day_of_month"] = dt_series.dt.day
    dim_date["day_name"] = dt_series.dt.strftime("%A")
    dim_date["is_weekend"] = dt_series.dt.dayofweek.isin([5, 6]).astype(int)
    dim_date["year_month_sort"] = dt_series.dt.strftime("%Y%m").astype(int)

    return dim_date


def generate_dim_plan() -> pd.DataFrame:
    """Create subscription plan dimension with pricing and billing intervals."""
    logger.info("Generating DimPlan...")
    plans = [
        {"plan_name": "Free", "billing_interval": "None", "price_usd": 0.00, "duration_days": 0, "tier_rank": 1},
        {"plan_name": "Weekly_Premium", "billing_interval": "Weekly", "price_usd": 3.99, "duration_days": 7, "tier_rank": 2},
        {"plan_name": "Monthly_Premium", "billing_interval": "Monthly", "price_usd": 9.99, "duration_days": 30, "tier_rank": 3},
        {"plan_name": "Annual_Premium", "billing_interval": "Annual", "price_usd": 59.99, "duration_days": 365, "tier_rank": 4},
    ]
    return pd.DataFrame(plans)


def prepare_star_schema(data_dir: str = "data/raw", out_dir: str = "data/processed"):
    """Prepare and export all Star Schema dimensional tables."""
    raw_path = Path(data_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    logger.info("Loading raw data from %s...", raw_path)
    users = pd.read_csv(raw_path / "users.csv")
    txns = pd.read_csv(raw_path / "transactions.csv")
    activity = pd.read_csv(raw_path / "user_activity.csv")

    # 1. DimUser
    logger.info("Transforming DimUser...")
    dim_user = users[[
        "user_id", "signup_date", "acquisition_channel", "country",
        "age_group", "device_type", "marketing_campaign",
        "onboarding_completed", "zodiac_sign", "subscription_plan"
    ]].copy()
    dim_user.rename(columns={"subscription_plan": "initial_plan"}, inplace=True)
    dim_user["onboarding_completed"] = dim_user["onboarding_completed"].map({True: "Completed", False: "Dropped Off"})
    dim_user_file = out_path / "DimUser.csv"
    dim_user.to_csv(dim_user_file, index=False)
    logger.info("Saved DimUser to %s (%d rows)", dim_user_file, len(dim_user))

    # 2. DimPlan
    dim_plan = generate_dim_plan()
    dim_plan_file = out_path / "DimPlan.csv"
    dim_plan.to_csv(dim_plan_file, index=False)
    logger.info("Saved DimPlan to %s (%d rows)", dim_plan_file, len(dim_plan))

    # 3. DimDate
    dim_date = generate_dim_date("2025-01-01", "2025-09-30")
    dim_date_file = out_path / "DimDate.csv"
    dim_date.to_csv(dim_date_file, index=False)
    logger.info("Saved DimDate to %s (%d rows)", dim_date_file, len(dim_date))

    # 4. FactTransactions
    logger.info("Transforming FactTransactions...")
    fact_txns = txns[[
        "transaction_id", "user_id", "transaction_date", "product_type",
        "amount", "currency", "payment_status", "refund_flag"
    ]].copy()
    fact_txns["refund_flag"] = fact_txns["refund_flag"].astype(int)
    fact_txns_file = out_path / "FactTransactions.csv"
    fact_txns.to_csv(fact_txns_file, index=False)
    logger.info("Saved FactTransactions to %s (%d rows)", fact_txns_file, len(fact_txns))

    # 5. FactActivity (Clean and export)
    logger.info("Transforming FactActivity...")
    fact_act = activity[[
        "event_id", "user_id", "event_date", "event_type",
        "feature_name", "session_duration_seconds", "notification_opened", "session_number"
    ]].copy()
    fact_act["notification_opened"] = fact_act["notification_opened"].astype(int)
    fact_act_file = out_path / "FactActivity.csv"
    fact_act.to_csv(fact_act_file, index=False)
    logger.info("Saved FactActivity to %s (%d rows)", fact_act_file, len(fact_act))

    # 6. Verify FactChurnPrediction exists (created by src/train_model.py)
    pred_file = out_path / "fact_churn_prediction.csv"
    if not pred_file.exists():
        logger.warning("fact_churn_prediction.csv not found in %s! Generating now...", out_path)
        from src.train_model import train_and_evaluate
        train_and_evaluate(data_dir, out_dir)

    logger.info("Star Schema dimensional preparation successfully complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare Power BI Star Schema tables.")
    parser.add_argument("--data-dir", type=str, default="data/raw")
    parser.add_argument("--out-dir", type=str, default="data/processed")
    args = parser.parse_args()

    prepare_star_schema(args.data_dir, args.out_dir)
