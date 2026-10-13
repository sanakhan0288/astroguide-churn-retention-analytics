"""
AstroGuide AI - Synthetic Data Validation Engine
================================================
Validates relational integrity, schema constraints, business rules,
null values, category consistency, and revenue reconciliation across
the synthetic datasets.

Author: AstroGuide Analytics Team
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


class DataValidator:
    """Validates relational tables for AstroGuide AI."""

    def __init__(self, data_dir: str = "data/raw"):
        self.data_dir = Path(data_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, any] = {}

    def load_data(self) -> Dict[str, pd.DataFrame]:
        """Load all raw CSV files into DataFrames."""
        tables = {}
        expected_files = [
            "users.csv",
            "subscriptions.csv",
            "transactions.csv",
            "user_activity.csv",
            "churn_labels.csv",
        ]
        for fname in expected_files:
            fpath = self.data_dir / fname
            if not fpath.exists():
                self.errors.append(f"Missing required file: {fpath}")
                continue
            tables[fname.replace(".csv", "")] = pd.read_csv(fpath)
            logger.info("Loaded %s: %d rows, %d columns", fname, len(tables[fname.replace(".csv", "")]), len(tables[fname.replace(".csv", "")].columns))
        return tables

    def validate_primary_keys(self, tables: Dict[str, pd.DataFrame]) -> bool:
        """Check uniqueness and non-nullness of primary keys."""
        pk_map = {
            "users": "user_id",
            "subscriptions": "subscription_id",
            "transactions": "transaction_id",
            "user_activity": "event_id",
            "churn_labels": "user_id",
        }
        passed = True
        for table_name, pk in pk_map.items():
            if table_name not in tables:
                continue
            df = tables[table_name]
            # Null check
            null_count = df[pk].isnull().sum()
            if null_count > 0:
                self.errors.append(f"[{table_name}] Primary key '{pk}' has {null_count} NULL values.")
                passed = False
            # Uniqueness check
            dup_count = df[pk].duplicated().sum()
            if dup_count > 0:
                self.errors.append(f"[{table_name}] Primary key '{pk}' has {dup_count} duplicate values.")
                passed = False
            else:
                logger.info("PK check passed for %s ('%s'): %d unique IDs.", table_name, pk, len(df))
        return passed

    def validate_foreign_keys(self, tables: Dict[str, pd.DataFrame]) -> bool:
        """Verify that all user_id references in child tables exist in users."""
        if "users" not in tables:
            return False
        user_ids = set(tables["users"]["user_id"])
        child_tables = ["subscriptions", "transactions", "user_activity", "churn_labels"]
        passed = True

        for child in child_tables:
            if child not in tables:
                continue
            df = tables[child]
            orphans = set(df["user_id"]) - user_ids
            if orphans:
                self.errors.append(
                    f"[{child}] Foreign key violation: {len(orphans)} user_id values do not exist in users table."
                )
                passed = False
            else:
                logger.info("FK check passed for %s: all user_ids valid.", child)
        return passed

    def validate_categories(self, tables: Dict[str, pd.DataFrame]) -> bool:
        """Ensure categorical fields adhere to controlled vocabularies."""
        passed = True
        allowed_channels = {"Organic Search", "Instagram Ads", "TikTok Ads", "Google Ads", "Referral"}
        allowed_devices = {"iOS", "Android", "Web"}
        allowed_plans = {"Free", "Weekly_Premium", "Monthly_Premium", "Annual_Premium"}
        allowed_payment_statuses = {"Success", "Failed", "Refunded"}

        if "users" in tables:
            channels = set(tables["users"]["acquisition_channel"].dropna())
            if not channels.issubset(allowed_channels):
                self.errors.append(f"[users] Unexpected channels: {channels - allowed_channels}")
                passed = False

            devices = set(tables["users"]["device_type"].dropna())
            if not devices.issubset(allowed_devices):
                self.errors.append(f"[users] Unexpected device types: {devices - allowed_devices}")
                passed = False

        if "subscriptions" in tables:
            sub_plans = set(tables["subscriptions"]["plan_name"].dropna())
            if not sub_plans.issubset(allowed_plans - {"Free"}):
                self.errors.append(f"[subscriptions] Unexpected plans: {sub_plans}")
                passed = False

        if "transactions" in tables:
            pay_stat = set(tables["transactions"]["payment_status"].dropna())
            if not pay_stat.issubset(allowed_payment_statuses):
                self.errors.append(f"[transactions] Unexpected payment status: {pay_stat - allowed_payment_statuses}")
                passed = False

        if passed:
            logger.info("Categorical value domain check passed for all tables.")
        return passed

    def validate_date_logic(self, tables: Dict[str, pd.DataFrame]) -> bool:
        """Verify chronological validity of dates and event timestamps."""
        passed = True
        if "subscriptions" in tables and "users" in tables:
            subs = tables["subscriptions"].merge(tables["users"][["user_id", "signup_date"]], on="user_id")
            invalid_start = subs[subs["subscription_start_date"] < subs["signup_date"]]
            if not invalid_start.empty:
                self.errors.append(f"[subscriptions] {len(invalid_start)} subscriptions start before user signup.")
                passed = False

            invalid_end = subs[
                (subs["subscription_end_date"].notnull()) &
                (subs["subscription_end_date"] < subs["subscription_start_date"])
            ]
            if not invalid_end.empty:
                self.errors.append(f"[subscriptions] {len(invalid_end)} subscriptions end before start date.")
                passed = False

        if "user_activity" in tables and "users" in tables:
            act = tables["user_activity"].merge(tables["users"][["user_id", "signup_date"]], on="user_id")
            invalid_act = act[act["event_date"] < act["signup_date"]]
            if not invalid_act.empty:
                self.errors.append(f"[user_activity] {len(invalid_act)} events occur before user signup.")
                passed = False

            # Check impossible session durations
            bad_dur = act[act["session_duration_seconds"] <= 0]
            if not bad_dur.empty:
                self.errors.append(f"[user_activity] {len(bad_dur)} events have duration <= 0.")
                passed = False

        if passed:
            logger.info("Chronological and date integrity checks passed.")
        return passed

    def validate_churn_and_revenue(self, tables: Dict[str, pd.DataFrame]) -> bool:
        """Analyze churn label balance and reconcile financial transactions."""
        passed = True
        if "churn_labels" in tables:
            churn_df = tables["churn_labels"]
            churn_counts = churn_df["churn_label"].value_counts(normalize=True)
            churn_rate = churn_counts.get(1, 0.0)
            self.metrics["churn_rate"] = float(churn_rate)
            logger.info("Churn label distribution: Retained (0)=%.2f%%, Churned (1)=%.2f%%",
                        (1 - churn_rate) * 100, churn_rate * 100)

            if not (0.15 <= churn_rate <= 0.85):
                self.warnings.append(f"Extreme churn rate: {churn_rate:.2%}")

        if "transactions" in tables:
            txns = tables["transactions"]
            gross_revenue = txns[txns["payment_status"] == "Success"]["amount"].sum()
            failed_volume = txns[txns["payment_status"] == "Failed"]["amount"].sum()
            refund_volume = txns[txns["refund_flag"] == True]["amount"].sum()
            net_revenue = gross_revenue - refund_volume

            self.metrics["gross_revenue"] = float(gross_revenue)
            self.metrics["refund_volume"] = float(refund_volume)
            self.metrics["net_revenue"] = float(net_revenue)
            self.metrics["failed_volume"] = float(failed_volume)

            logger.info("Revenue Reconciliation:")
            logger.info("  Gross Success Revenue: $%.2f", gross_revenue)
            logger.info("  Refunded Amount:       $%.2f", refund_volume)
            logger.info("  Net Realized Revenue:  $%.2f", net_revenue)
            logger.info("  Failed Payments (excluded): $%.2f", failed_volume)

            # Ensure failed payments are not marked as refund_flag = True or counted in revenue
            inconsistent_failed = txns[(txns["payment_status"] == "Failed") & (txns["refund_flag"] == True)]
            if not inconsistent_failed.empty:
                self.errors.append(f"[transactions] {len(inconsistent_failed)} failed transactions incorrectly flagged as refunds.")
                passed = False

        return passed

    def run_all(self) -> Tuple[bool, Dict[str, any]]:
        """Execute full validation suite."""
        logger.info("Starting comprehensive data validation suite...")
        tables = self.load_data()
        if not tables or self.errors:
            return False, {"errors": self.errors, "warnings": self.warnings}

        self.validate_primary_keys(tables)
        self.validate_foreign_keys(tables)
        self.validate_categories(tables)
        self.validate_date_logic(tables)
        self.validate_churn_and_revenue(tables)

        is_valid = len(self.errors) == 0
        if is_valid:
            logger.info("✅ All validation checks PASSED successfully!")
        else:
            logger.error("❌ Validation FAILED with %d errors:", len(self.errors))
            for err in self.errors:
                logger.error("  - %s", err)

        return is_valid, {
            "is_valid": is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


def main():
    parser = argparse.ArgumentParser(description="Validate AstroGuide AI synthetic data.")
    parser.add_argument("--data-dir", type=str, default="data/raw", help="Directory containing CSV files")
    args = parser.parse_args()

    validator = DataValidator(args.data_dir)
    is_valid, report = validator.run_all()
    if not is_valid:
        sys.exit(1)


if __name__ == "__main__":
    main()
