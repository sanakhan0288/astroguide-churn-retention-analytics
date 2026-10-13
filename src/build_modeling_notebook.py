"""
AstroGuide AI - Modeling Notebook Builder
=========================================
Generates notebooks/03_churn_prediction.ipynb documenting the end-to-end
leakage-free predictive modeling workflow.
"""

import json
from pathlib import Path

notebook_content = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# AstroGuide AI — Customer Churn Prediction Modeling\n",
                "## 1. Problem Framing & Business Objective\n",
                "Customer churn causes revenue loss and raises Customer Acquisition Cost (CAC). The goal of this model is **early detection**: identifying users at high risk of becoming inactive in the next 30 days so the lifecycle marketing team can deploy targeted retention campaigns (personalized push notifications, renewal incentives).\n",
                "\n",
                "> **Zero-Leakage Protocol:** Features are strictly computed from data observable on or before the cutoff date ($t_0 = 2025-08-31$). Churn is defined as zero sessions in the forward outcome window ($2025-09-01$ to $2025-09-30$)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import numpy as np\n",
                "import pandas as pd\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from sklearn.model_selection import train_test_split\n",
                "from sklearn.compose import ColumnTransformer\n",
                "from sklearn.pipeline import Pipeline\n",
                "from sklearn.preprocessing import StandardScaler, OneHotEncoder\n",
                "from sklearn.dummy import DummyClassifier\n",
                "from sklearn.linear_model import LogisticRegression\n",
                "from sklearn.ensemble import RandomForestClassifier\n",
                "from sklearn.metrics import (\n",
                "    accuracy_score, precision_score, recall_score, f1_score,\n",
                "    roc_auc_score, confusion_matrix, classification_report, roc_curve\n",
                ")\n",
                "import sys\n",
                "sys.path.append('..')\n",
                "from src.features import build_features\n",
                "\n",
                "plt.style.use('seaborn-v0_8-whitegrid')\n",
                "plt.rcParams['figure.figsize'] = (8, 5)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Feature Matrix Construction & Train/Test Split\n",
                "Extracting point-in-time behavioral, demographic, and financial features up to August 31, 2025."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "df = build_features('../data/raw' if Path('../data/raw').exists() else 'data/raw')\n",
                "print(f'Feature Matrix: {df.shape[0]:,} users, {df.shape[1]} columns')\n",
                "display(df.head(3))\n",
                "\n",
                "X = df.drop(columns=['user_id', 'churn_label'])\n",
                "y = df['churn_label']\n",
                "user_ids = df['user_id']\n",
                "\n",
                "X_train, X_test, y_train, y_test, u_train, u_test = train_test_split(\n",
                "    X, y, user_ids, test_size=0.20, random_state=42, stratify=y\n",
                ")\n",
                "print(f'Train Set: {len(X_train):,} samples | Test Set: {len(X_test):,} samples')\n",
                "print(f'Baseline Churn Rate: {y_train.mean():.2%}')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Preprocessing Pipeline Design\n",
                "Preventing data leakage by applying transformations inside a scikit-learn pipeline: scaling numerical features and one-hot encoding categorical variables, fitted strictly on training data."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "categorical_cols = ['acquisition_channel', 'country', 'age_group', 'device_type', 'subscription_plan']\n",
                "numerical_cols = [c for c in X.columns if c not in categorical_cols]\n",
                "\n",
                "preprocessor = ColumnTransformer(\n",
                "    transformers=[\n",
                "        ('num', StandardScaler(), numerical_cols),\n",
                "        ('cat', OneHotEncoder(drop='first', handle_unknown='ignore', sparse_output=False), categorical_cols)\n",
                "    ]\n",
                ")\n",
                "print(f'Numerical Features ({len(numerical_cols)}):', numerical_cols)\n",
                "print(f'Categorical Features ({len(categorical_cols)}):', categorical_cols)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Model Training & Baseline Benchmarking\n",
                "1. **Baseline Model:** DummyClassifier (predicts the majority class). Demonstrates why accuracy alone can be misleading.\n",
                "2. **Primary Model:** Logistic Regression with `class_weight='balanced'`.\n",
                "3. **Benchmark:** Random Forest Classifier (evaluating non-linear decision boundaries)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# 1. Dummy Baseline\n",
                "dummy_pipe = Pipeline([('prep', preprocessor), ('clf', DummyClassifier(strategy='most_frequent'))])\n",
                "dummy_pipe.fit(X_train, y_train)\n",
                "\n",
                "# 2. Logistic Regression\n",
                "log_pipe = Pipeline([('prep', preprocessor), ('clf', LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'))])\n",
                "log_pipe.fit(X_train, y_train)\n",
                "\n",
                "# 3. Random Forest\n",
                "rf_pipe = Pipeline([('prep', preprocessor), ('clf', RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight='balanced'))])\n",
                "rf_pipe.fit(X_train, y_train)\n",
                "print('All models trained successfully!')"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Comprehensive Model Evaluation & Confusion Matrix\n",
                "Comparing models across Precision, Recall, F1-Score, and ROC-AUC."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "models = {\n",
                "    'Dummy Baseline': dummy_pipe,\n",
                "    'Logistic Regression': log_pipe,\n",
                "    'Random Forest': rf_pipe\n",
                "}\n",
                "\n",
                "metrics = []\n",
                "for name, pipe in models.items():\n",
                "    preds = pipe.predict(X_test)\n",
                "    probs = pipe.predict_proba(X_test)[:, 1] if hasattr(pipe, 'predict_proba') else None\n",
                "    metrics.append({\n",
                "        'Model': name,\n",
                "        'Accuracy': accuracy_score(y_test, preds),\n",
                "        'Precision': precision_score(y_test, preds, zero_division=0),\n",
                "        'Recall': recall_score(y_test, preds, zero_division=0),\n",
                "        'F1-Score': f1_score(y_test, preds, zero_division=0),\n",
                "        'ROC-AUC': roc_auc_score(y_test, probs) if probs is not None else 0.50\n",
                "    })\n",
                "\n",
                "metrics_df = pd.DataFrame(metrics)\n",
                "display(metrics_df)\n",
                "\n",
                "# Confusion Matrix for Logistic Regression\n",
                "cm = confusion_matrix(y_test, log_pipe.predict(X_test))\n",
                "fig, ax = plt.subplots(figsize=(6, 4.5))\n",
                "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, ax=ax,\n",
                "            xticklabels=['Retained (0)', 'Churned (1)'], yticklabels=['Retained (0)', 'Churned (1)'])\n",
                "ax.set_title('Logistic Regression — Confusion Matrix', fontsize=12, fontweight='bold')\n",
                "ax.set_ylabel('Actual Label')\n",
                "ax.set_xlabel('Predicted Label')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Business Trade-Off Analysis: False Positives vs. False Negatives\n",
                "* **False Negative (FN):** Model predicts user will stay, but they churn. **Cost:** Lost subscription revenue ($40–$60 LTV) and lost customer relationship.\n",
                "* **False Positive (FP):** Model predicts user will churn, but they would stay. **Cost:** Cost of marketing message or promotional discount ($1–$3 push promo discount).\n",
                "* **Business Conclusion:** For a consumer subscription app, **Recall is prioritized over Precision**. Missing a customer costs far more than sending an unnecessary discount push notification."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 7. Model Interpretability — Top Churn Drivers\n",
                "Examining the logistic regression coefficients to diagnose why users churn."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "cat_encoded = log_pipe.named_steps['prep'].named_transformers_['cat'].get_feature_names_out(categorical_cols).tolist()\n",
                "all_feature_names = numerical_cols + cat_encoded\n",
                "coefs = log_pipe.named_steps['clf'].coef_[0]\n",
                "\n",
                "importance_df = pd.DataFrame({\n",
                "    'Feature': all_feature_names,\n",
                "    'Coefficient': coefs,\n",
                "    'Abs_Weight': np.abs(coefs)\n",
                "}).sort_values('Abs_Weight', ascending=False)\n",
                "\n",
                "fig, ax = plt.subplots(figsize=(9, 5))\n",
                "top10 = importance_df.head(10).sort_values('Coefficient')\n",
                "colors = ['#27ae60' if c < 0 else '#e74c3c' for c in top10['Coefficient']]\n",
                "ax.barh(top10['Feature'], top10['Coefficient'], color=colors)\n",
                "ax.set_title('Top 10 Feature Coefficients (Green = Reduces Churn, Red = Increases Churn)', fontsize=12, fontweight='bold')\n",
                "ax.set_xlabel('Standardized Logistic Regression Coefficient')\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 8. Customer Risk Tiering & Export for Power BI\n",
                "Exporting predicted probabilities segmented into action-ready operational tiers: High Risk ($\ge 70\\%$), Medium Risk ($40-69\\%$), and Low Risk ($<40\\%$)."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "export_df = pd.read_csv('../data/processed/fact_churn_prediction.csv' if Path('../data/processed/fact_churn_prediction.csv').exists() else 'data/processed/fact_churn_prediction.csv')\n",
                "display(export_df['risk_tier'].value_counts(normalize=True).mul(100).round(2).rename('Cohort Share (%)'))\n",
                "display(export_df.head(5))"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3 (.venv)",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbformat": 4,
            "nbformat_minor": 2
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

out_notebook = Path("notebooks/03_churn_prediction.ipynb")
with open(out_notebook, "w", encoding="utf-8") as f:
    json.dump(notebook_content, f, indent=2)

print(f"Jupyter Notebook successfully written to {out_notebook}")
