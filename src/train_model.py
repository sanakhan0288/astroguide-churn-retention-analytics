"""
AstroGuide AI - Leakage-Aware Churn Prediction Model
====================================================
Trains and evaluates baseline and production-grade ML models to predict customer
churn. Evaluates using Precision, Recall, F1, and ROC-AUC, analyzes feature
coefficients, and exports risk-scored customer tiers for Power BI.

Author: AstroGuide Analytics Team
Seed: 42 (Reproducible)
"""

import argparse
import logging
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.features import build_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def prepare_datasets(df: pd.DataFrame, test_size: float = 0.20, random_state: int = 42):
    """
    Split features and target strictly into train and test sets.
    Preserves user_id for evaluation mapping.
    """
    logger.info("Splitting dataset (test_size=%.2f, random_state=%d)...", test_size, random_state)

    X = df.drop(columns=["user_id", "churn_label"])
    y = df["churn_label"]
    user_ids = df["user_id"]

    X_train, X_test, y_train, y_test, u_train, u_test = train_test_split(
        X, y, user_ids, test_size=test_size, random_state=random_state, stratify=y
    )

    logger.info("Train set: %d samples (Churn: %.2f%%)", len(y_train), y_train.mean() * 100)
    logger.info("Test set:  %d samples (Churn: %.2f%%)", len(y_test), y_test.mean() * 100)
    return X_train, X_test, y_train, y_test, u_train, u_test, X.columns.tolist()


def build_preprocessor(numerical_cols: list, categorical_cols: list) -> ColumnTransformer:
    """Build scikit-learn ColumnTransformer fitting strictly on train data."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numerical_cols),
            ("cat", OneHotEncoder(drop="first", handle_unknown="ignore", sparse_output=False), categorical_cols),
        ]
    )
    return preprocessor


def evaluate_model(name: str, y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray = None):
    """Compute and format standardized evaluation metrics."""
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, y_prob) if y_prob is not None else 0.50
    cm = confusion_matrix(y_true, y_pred)

    print("\n" + "=" * 65)
    print(f"EVALUATION: {name}")
    print("=" * 65)
    print(f"Accuracy:        {acc:.4f}  (Can be misleading in imbalanced datasets)")
    print(f"Precision:       {prec:.4f}  (Of all users predicted to churn, how many actually did?)")
    print(f"Recall:          {rec:.4f}  (Of all users who actually churned, how many did we catch?)")
    print(f"F1-Score:        {f1:.4f}  (Harmonic mean of precision and recall)")
    print(f"ROC-AUC:         {auc:.4f}  (Ranking discriminative ability)")
    print("-" * 65)
    print(f"Confusion Matrix (TN: {cm[0,0]}, FP: {cm[0,1]}, FN: {cm[1,0]}, TP: {cm[1,1]}):")
    print(f"  [TN={cm[0,0]:<5}  FP={cm[0,1]:<5}] (Actual Retained)")
    print(f"  [FN={cm[1,0]:<5}  TP={cm[1,1]:<5}] (Actual Churned)")
    print("=" * 65)

    return {"model": name, "accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "roc_auc": auc}


def train_and_evaluate(data_dir: str = "data/raw", output_dir: str = "data/processed"):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Feature Engineering
    features = build_features(data_dir)

    # Define Column Types
    categorical_cols = [
        "acquisition_channel", "country", "age_group",
        "device_type", "subscription_plan"
    ]
    numerical_cols = [col for col in features.columns if col not in categorical_cols + ["user_id", "churn_label"]]

    X_train, X_test, y_train, y_test, u_train, u_test, all_features = prepare_datasets(features)
    preprocessor = build_preprocessor(numerical_cols, categorical_cols)

    # 2. Baseline Model (Dummy Most Frequent)
    dummy_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", DummyClassifier(strategy="most_frequent")),
    ])
    dummy_pipe.fit(X_train, y_train)
    y_pred_dummy = dummy_pipe.predict(X_test)
    y_prob_dummy = dummy_pipe.predict_proba(X_test)[:, 1]
    res_dummy = evaluate_model("Baseline (Majority Class Dummy)", y_test, y_pred_dummy, y_prob_dummy)

    # 3. Logistic Regression Model (Primary, Interpretable)
    log_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42, class_weight="balanced")),
    ])
    log_pipe.fit(X_train, y_train)
    y_pred_log = log_pipe.predict(X_test)
    y_prob_log = log_pipe.predict_proba(X_test)[:, 1]
    res_log = evaluate_model("Logistic Regression (Balanced)", y_test, y_pred_log, y_prob_log)

    # 4. Random Forest Benchmark (Optional Tree-Based Comparison)
    rf_pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight="balanced")),
    ])
    rf_pipe.fit(X_train, y_train)
    y_pred_rf = rf_pipe.predict(X_test)
    y_prob_rf = rf_pipe.predict_proba(X_test)[:, 1]
    res_rf = evaluate_model("Random Forest Classifier (Benchmark)", y_test, y_pred_rf, y_prob_rf)

    # 5. Feature Importance / Coefficients Analysis
    cat_feature_names = log_pipe.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out(categorical_cols).tolist()
    feature_names = numerical_cols + cat_feature_names
    coefficients = log_pipe.named_steps["classifier"].coef_[0]

    coef_df = pd.DataFrame({
        "Feature": feature_names,
        "Coefficient": coefficients,
        "Abs_Impact": np.abs(coefficients),
    }).sort_values("Abs_Impact", ascending=False)

    print("\nTOP 10 LOGISTIC REGRESSION CHURN DRIVERS (COEFFICIENTS):")
    print(coef_df.head(10)[["Feature", "Coefficient"]].to_string(index=False))

    # 6. Generate Risk Scoring Dataset for Entire Cohort (Power BI Ingestion)
    logger.info("Generating customer churn risk scores for entire cohort...")
    full_X = features.drop(columns=["user_id", "churn_label"])
    full_probs = log_pipe.predict_proba(full_X)[:, 1]
    full_preds = log_pipe.predict(full_X)

    # Segment into Risk Categories
    risk_tiers = pd.cut(
        full_probs,
        bins=[-0.01, 0.40, 0.70, 1.01],
        labels=["Low Risk (<40%)", "Medium Risk (40-69%)", "High Risk (>=70%)"]
    )

    churn_export = pd.DataFrame({
        "user_id": features["user_id"],
        "churn_label": features["churn_label"],
        "predicted_churn": full_preds,
        "churn_probability": np.round(full_probs, 4),
        "risk_tier": risk_tiers,
        "tenure_days": features["tenure_days"],
        "days_since_last_session": features["days_since_last_session"],
        "sessions_last_30d": features["sessions_last_30d"],
        "historical_net_spend": features["historical_net_spend"],
    })

    export_file = out_path / "fact_churn_prediction.csv"
    churn_export.to_csv(export_file, index=False)
    logger.info("Exported risk scoring dataset to %s (%d rows)", export_file, len(churn_export))

    # Save trained model pipeline artifact
    model_artifact = out_path / "churn_model_pipeline.pkl"
    joblib.dump(log_pipe, model_artifact)
    logger.info("Saved trained pipeline model to %s", model_artifact)

    return res_dummy, res_log, res_rf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train churn prediction model.")
    parser.add_argument("--data-dir", type=str, default="data/raw")
    parser.add_argument("--output-dir", type=str, default="data/processed")
    args = parser.parse_args()

    train_and_evaluate(args.data_dir, args.output_dir)
