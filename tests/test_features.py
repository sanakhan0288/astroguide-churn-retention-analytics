"""
AstroGuide AI - Automated Tests for Feature Engineering & Leakage Prevention
============================================================================
Pytest suite verifying feature matrix integrity, absence of nulls,
correct target assignment, and strict zero-leakage constraints.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.features import build_features, CUTOFF_STR


@pytest.fixture(scope="module")
def features_df():
    return build_features("data/raw")


def test_feature_matrix_shape(features_df):
    """Assert feature matrix contains all 10,000 users and required feature columns."""
    assert len(features_df) == 10000, f"Expected 10,000 users, got {len(features_df)}"
    assert "user_id" in features_df.columns
    assert "churn_label" in features_df.columns
    assert "tenure_days" in features_df.columns
    assert "days_since_last_session" in features_df.columns


def test_no_null_values(features_df):
    """Assert no null values exist in numerical or categorical features."""
    null_counts = features_df.isnull().sum()
    assert null_counts.sum() == 0, f"Found null values in feature matrix: {null_counts[null_counts > 0]}"


def test_tenure_minimum_boundary(features_df):
    """Assert all cohort users have at least 31 days of tenure prior to cutoff."""
    assert (features_df["tenure_days"] >= 31).all(), "Found users with less than 31 days tenure."


def test_recency_non_negative(features_df):
    """Assert days since last session is strictly non-negative (no future sessions logged)."""
    assert (features_df["days_since_last_session"] >= 0).all(), "Found negative days_since_last_session (future leakage)."


def test_target_label_distribution(features_df):
    """Assert target label is strictly binary and well-distributed."""
    unique_labels = set(features_df["churn_label"].unique())
    assert unique_labels == {0, 1}, f"Unexpected target labels: {unique_labels}"
    churn_rate = features_df["churn_label"].mean()
    assert 0.35 <= churn_rate <= 0.55, f"Unexpected churn rate: {churn_rate:.2%}"


def test_leakage_isolation(monkeypatch, tmp_path):
    """
    Simulate altering post-cutoff event telemetry (events in September 2025).
    Verify that post-cutoff changes produce IDENTICAL feature matrices, proving zero leakage.
    """
    raw_dir = Path("data/raw")
    temp_dir = tmp_path / "mock_raw"
    temp_dir.mkdir()

    # Copy raw tables
    for fname in ["users.csv", "subscriptions.csv", "transactions.csv", "churn_labels.csv"]:
        (temp_dir / fname).write_text((raw_dir / fname).read_text())

    # Load activity and add fake future events after cutoff (Sept 15, 2025)
    act_df = pd.read_csv(raw_dir / "user_activity.csv")
    future_events = act_df.head(100).copy()
    future_events["event_date"] = "2025-09-15"
    future_events["event_id"] = [f"FAKE_EVT_{i}" for i in range(len(future_events))]

    act_modified = pd.concat([act_df, future_events], ignore_index=True)
    act_modified.to_csv(temp_dir / "user_activity.csv", index=False)

    # Build features on original vs modified
    original_features = build_features(str(raw_dir))
    tampered_features = build_features(str(temp_dir))

    # Features before cutoff MUST be exactly identical
    pd.testing.assert_frame_equal(
        original_features.drop(columns=["user_id"]),
        tampered_features.drop(columns=["user_id"]),
        check_dtype=True
    )
