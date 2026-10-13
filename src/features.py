"""
AstroGuide AI - Leakage-Free Feature Engineering
================================================
Constructs a point-in-time analytical feature dataset for churn prediction.
All features are strictly evaluated up to the observation cutoff date (t_0 = 2025-08-31).
Zero future information or post-cutoff telemetry is utilized.

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

CUTOFF_DATE = datetime(2025, 8, 31)
CUTOFF_STR = "2025-08-31"


def build_features(data_dir: str = "data/raw") -> pd.DataFrame:
    """
    Extract and engineer point-in-time features strictly prior to or on CUTOFF_DATE.

    Parameters:
    -----------
    data_dir : str
        Directory containing raw CSV tables.

    Returns:
    --------
    pd.DataFrame
        Analytical feature matrix (one row per user) ready for train/test split.
    """
    data_path = Path(data_dir)
    logger.info("Building point-in-time features with cutoff date: %s", CUTOFF_STR)

    users = pd.read_csv(data_path / "users.csv")
    subs = pd.read_csv(data_path / "subscriptions.csv")
    txns = pd.read_csv(data_path / "transactions.csv")
    activity = pd.read_csv(data_path / "user_activity.csv")
    churn = pd.read_csv(data_path / "churn_labels.csv")

    # 1. Base User Demographics & Tenure
    users["signup_dt"] = pd.to_datetime(users["signup_date"])
    users["tenure_days"] = (CUTOFF_DATE - users["signup_dt"]).dt.days
    users["onboarding_completed"] = users["onboarding_completed"].astype(int)

    feature_df = users[[
        "user_id", "acquisition_channel", "country", "age_group",
        "device_type", "onboarding_completed", "subscription_plan", "tenure_days"
    ]].copy()

    # 2. Financial History Prior to Cutoff
    txns_pre = txns[txns["transaction_date"] <= CUTOFF_STR].copy()
    success_txns = txns_pre[txns_pre["payment_status"] == "Success"]
    refund_txns = txns_pre[txns_pre["refund_flag"] == True]

    spend_by_user = success_txns.groupby("user_id")["amount"].sum().rename("gross_spend")
    refund_by_user = refund_txns.groupby("user_id")["amount"].sum().rename("refund_spend")
    txn_count_by_user = success_txns.groupby("user_id")["transaction_id"].count().rename("successful_txns_count")

    fin_metrics = pd.concat([spend_by_user, refund_by_user, txn_count_by_user], axis=1).fillna(0)
    fin_metrics["historical_net_spend"] = fin_metrics["gross_spend"] - fin_metrics["refund_spend"]

    feature_df = feature_df.merge(
        fin_metrics[["historical_net_spend", "successful_txns_count"]],
        on="user_id", how="left"
    )
    feature_df["historical_net_spend"] = feature_df["historical_net_spend"].fillna(0.0)
    feature_df["successful_txns_count"] = feature_df["successful_txns_count"].fillna(0).astype(int)

    # 3. Subscription Status at Cutoff
    # Only consider subscriptions started on or before cutoff
    subs_pre = subs[subs["subscription_start_date"] <= CUTOFF_STR].copy()
    
    # Active subscription at cutoff: either active, or cancellation date is AFTER cutoff
    active_at_cutoff = subs_pre[
        (subs_pre["subscription_status"] == "Active") |
        (subs_pre["cancellation_date"] > CUTOFF_STR)
    ]["user_id"].unique()

    # Cancelled before or on cutoff
    cancelled_pre_cutoff = subs_pre[
        (subs_pre["cancellation_date"].notnull()) &
        (subs_pre["cancellation_date"] <= CUTOFF_STR)
    ]["user_id"].unique()

    feature_df["active_sub_at_cutoff"] = feature_df["user_id"].isin(active_at_cutoff).astype(int)
    feature_df["cancelled_prior_to_cutoff"] = feature_df["user_id"].isin(cancelled_pre_cutoff).astype(int)

    # 4. Behavioral Telemetry Features (Pre-Cutoff Only)
    # Strictly filter events <= CUTOFF_STR
    act_pre = activity[activity["event_date"] <= CUTOFF_STR].copy()
    act_pre["event_dt"] = pd.to_datetime(act_pre["event_date"])
    act_pre["days_to_cutoff"] = (CUTOFF_DATE - act_pre["event_dt"]).dt.days

    # Recency: Days since most recent session
    most_recent_act = act_pre.groupby("user_id")["days_to_cutoff"].min().rename("days_since_last_session")
    feature_df = feature_df.merge(most_recent_act, on="user_id", how="left")
    # If user never logged an event before cutoff, impute with user tenure
    feature_df["days_since_last_session"] = feature_df["days_since_last_session"].fillna(feature_df["tenure_days"])

    # Final 7 Days Engagement Window (Days 0 to 6 before cutoff)
    act_7d = act_pre[act_pre["days_to_cutoff"] <= 6]
    sessions_7d = act_7d.groupby("user_id")["session_number"].nunique().rename("sessions_last_7d")
    events_7d = act_7d.groupby("user_id")["event_id"].count().rename("events_last_7d")

    # Final 30 Days Engagement Window (Days 0 to 29 before cutoff)
    act_30d = act_pre[act_pre["days_to_cutoff"] <= 29]
    sessions_30d = act_30d.groupby("user_id")["session_number"].nunique().rename("sessions_last_30d")
    events_30d = act_30d.groupby("user_id")["event_id"].count().rename("events_last_30d")
    avg_dur_30d = act_30d.groupby("user_id")["session_duration_seconds"].mean().rename("avg_duration_sec_30d")
    unique_features_30d = act_30d.groupby("user_id")["feature_name"].nunique().rename("unique_features_30d")

    # Notification & AI Chat engagement in last 30 days
    notif_30d = act_30d[act_30d["notification_opened"] == True].groupby("user_id")["event_id"].count().rename("notif_opened_30d")
    ai_chat_30d = act_30d[act_30d["feature_name"] == "AI_Chat"].groupby("user_id")["event_id"].count().rename("ai_chat_events_30d")

    # Merge Telemetry Features
    telem_metrics = pd.concat([
        sessions_7d, events_7d, sessions_30d, events_30d,
        avg_dur_30d, unique_features_30d, notif_30d, ai_chat_30d
    ], axis=1).fillna(0)

    feature_df = feature_df.merge(telem_metrics, on="user_id", how="left").fillna(0)

    # 5. Attach Ground-Truth Churn Target
    feature_df = feature_df.merge(churn[["user_id", "churn_label"]], on="user_id")

    logger.info("Constructed feature dataset for %d users across %d columns.", len(feature_df), len(feature_df.columns))
    return feature_df


def main():
    parser = argparse.ArgumentParser(description="Generate leakage-free features for churn prediction.")
    parser.add_argument("--data-dir", type=str, default="data/raw", help="Directory with raw CSVs")
    parser.add_argument("--output-file", type=str, default="data/processed/churn_features.csv", help="Target features file")
    args = parser.parse_args()

    out_path = Path(args.output_file)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    features = build_features(args.data_dir)
    features.to_csv(out_path, index=False)
    logger.info("Successfully exported features to %s (%d rows, %d cols)", out_path, len(features), len(features.columns))


if __name__ == "__main__":
    main()
