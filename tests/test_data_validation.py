"""
AstroGuide AI - Automated Data Quality & Validation Tests
=========================================================
Pytest suite verifying schema integrity, referential integrity,
domain constraints, and financial reconciliation for synthetic datasets.
"""

from pathlib import Path
import pandas as pd
import pytest

DATA_DIR = Path("data/raw")


@pytest.fixture(scope="module")
def users_df():
    return pd.read_csv(DATA_DIR / "users.csv")


@pytest.fixture(scope="module")
def subs_df():
    return pd.read_csv(DATA_DIR / "subscriptions.csv")


@pytest.fixture(scope="module")
def txns_df():
    return pd.read_csv(DATA_DIR / "transactions.csv")


@pytest.fixture(scope="module")
def activity_df():
    return pd.read_csv(DATA_DIR / "user_activity.csv")


@pytest.fixture(scope="module")
def churn_df():
    return pd.read_csv(DATA_DIR / "churn_labels.csv")


def test_files_exist():
    """Verify all 5 synthetic relational CSV files exist."""
    required = ["users.csv", "subscriptions.csv", "transactions.csv", "user_activity.csv", "churn_labels.csv"]
    for f in required:
        assert (DATA_DIR / f).exists(), f"Expected file {f} was not found."


def test_users_primary_key(users_df):
    """Assert user_id is strictly unique and contains no null values."""
    assert users_df["user_id"].isnull().sum() == 0, "user_id contains nulls."
    assert users_df["user_id"].duplicated().sum() == 0, "user_id contains duplicates."
    assert len(users_df) >= 5000, "Dataset contains fewer than 5,000 users."


def test_foreign_key_integrity(users_df, subs_df, txns_df, activity_df, churn_df):
    """Assert all user_id values in child tables exist in the parent users table."""
    valid_users = set(users_df["user_id"])
    assert set(subs_df["user_id"]).issubset(valid_users), "Orphan users in subscriptions."
    assert set(txns_df["user_id"]).issubset(valid_users), "Orphan users in transactions."
    assert set(activity_df["user_id"]).issubset(valid_users), "Orphan users in user_activity."
    assert set(churn_df["user_id"]).issubset(valid_users), "Orphan users in churn_labels."


def test_activity_durations_positive(activity_df):
    """Assert all session durations are strictly positive."""
    assert (activity_df["session_duration_seconds"] > 0).all(), "Found non-positive durations."


def test_chronological_consistency(users_df, activity_df, subs_df):
    """Assert activities and subscriptions do not precede user signup date."""
    act_merged = activity_df.merge(users_df[["user_id", "signup_date"]], on="user_id")
    assert (act_merged["event_date"] >= act_merged["signup_date"]).all(), "Events found before user signup."

    subs_merged = subs_df.merge(users_df[["user_id", "signup_date"]], on="user_id")
    assert (subs_merged["subscription_start_date"] >= subs_merged["signup_date"]).all(), "Subscription started before signup."


def test_churn_label_distribution(churn_df):
    """Assert churn rate is realistic (between 30% and 60%)."""
    churn_rate = churn_df["churn_label"].mean()
    assert 0.30 <= churn_rate <= 0.60, f"Unrealistic churn rate: {churn_rate:.2%}"


def test_revenue_logic(txns_df):
    """Assert financial calculations correctly distinguish success, refunds, and failed charges."""
    # Failed charges must not be marked as refunded
    failed_refunded = txns_df[(txns_df["payment_status"] == "Failed") & (txns_df["refund_flag"] == True)]
    assert len(failed_refunded) == 0, "Failed charges should not have refund_flag=True."

    gross_success = txns_df[txns_df["payment_status"] == "Success"]["amount"].sum()
    refunds = txns_df[txns_df["refund_flag"] == True]["amount"].sum()
    assert gross_success > refunds, "Refunds exceed gross revenue."
    assert gross_success > 0, "Gross revenue is zero."
