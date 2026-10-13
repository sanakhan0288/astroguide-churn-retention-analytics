"""
AstroGuide AI - Exploratory Data Analysis & Visualizations Engine
=================================================================
Analyzes customer demographics, feature engagement, subscription retention,
and revenue performance. Generates publication-ready figures for executive
reporting and validates core business hypotheses.

Author: AstroGuide Analytics Team
"""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Set style aesthetics
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "Helvetica", "Arial", "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8

FIGURES_DIR = Path("reports/figures")
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path("data/raw")


def load_datasets():
    """Load all raw relational tables."""
    logger.info("Loading datasets from %s...", DATA_DIR)
    users = pd.read_csv(DATA_DIR / "users.csv")
    subs = pd.read_csv(DATA_DIR / "subscriptions.csv")
    txns = pd.read_csv(DATA_DIR / "transactions.csv")
    activity = pd.read_csv(DATA_DIR / "user_activity.csv")
    churn = pd.read_csv(DATA_DIR / "churn_labels.csv")
    return users, subs, txns, activity, churn


def run_eda():
    users, subs, txns, activity, churn = load_datasets()

    # Merge churn label into users
    user_master = users.merge(churn[["user_id", "churn_label", "outcome_sessions_count"]], on="user_id")

    # 1. Overall Churn Distribution
    logger.info("Analyzing overall churn distribution...")
    churn_counts = user_master["churn_label"].value_counts()
    churn_rate = user_master["churn_label"].mean()

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(["Retained (0)", "Churned (1)"], churn_counts.values, color=["#2ecc71", "#e74c3c"], width=0.5)
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval + 100, f"{yval:,} ({yval/len(user_master):.1%})",
                ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title("AstroGuide AI - Customer Churn vs. Retention Distribution", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("User Count", fontsize=11)
    ax.set_ylim(0, max(churn_counts.values) * 1.15)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "churn_distribution.png", dpi=300)
    plt.close()

    # 2. Churn Rate by Acquisition Channel
    logger.info("Analyzing churn by acquisition channel...")
    channel_summary = user_master.groupby("acquisition_channel")["churn_label"].agg(["count", "mean"]).reset_index()
    channel_summary.columns = ["acquisition_channel", "total_users", "churn_rate"]
    channel_summary = channel_summary.sort_values("churn_rate", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(channel_summary["acquisition_channel"], channel_summary["churn_rate"] * 100, color="#3498db")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 1, bar.get_y() + bar.get_height() / 2, f"{w:.1f}%", ha="left", va="center", fontsize=10, fontweight="bold")
    ax.set_title("Customer Churn Rate by Acquisition Channel", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Churn Rate (%)", fontsize=11)
    ax.set_xlim(0, 100)
    ax.axvline(churn_rate * 100, color="#e74c3c", linestyle="--", linewidth=1.5, label=f"Average Churn ({churn_rate:.1%})")
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "churn_by_channel.png", dpi=300)
    plt.close()

    # 3. Churn by Subscription Plan
    logger.info("Analyzing churn by subscription plan...")
    plan_summary = user_master.groupby("subscription_plan")["churn_label"].agg(["count", "mean"]).reset_index()
    plan_summary.columns = ["subscription_plan", "total_users", "churn_rate"]
    plan_summary = plan_summary.sort_values("churn_rate", ascending=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(plan_summary["subscription_plan"], plan_summary["churn_rate"] * 100, color="#9b59b6", width=0.5)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1, f"{h:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Churn Rate by Initial Subscription Plan", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Churn Rate (%)", fontsize=11)
    ax.set_ylim(0, 100)
    ax.axhline(churn_rate * 100, color="#e74c3c", linestyle="--", label=f"Average ({churn_rate:.1%})")
    ax.legend()
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "churn_by_plan.png", dpi=300)
    plt.close()

    # 4. Onboarding Completion vs. Churn Rate
    logger.info("Analyzing onboarding impact...")
    onboard_summary = user_master.groupby("onboarding_completed")["churn_label"].agg(["count", "mean"]).reset_index()
    onboard_summary["label"] = onboard_summary["onboarding_completed"].map({True: "Completed Onboarding", False: "Dropped Off Onboarding"})

    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(onboard_summary["label"], onboard_summary["mean"] * 100, color=["#e67e22", "#27ae60"], width=0.45)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 1.5, f"{h:.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title("Impact of Onboarding Completion on Churn Rate", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Churn Rate (%)", fontsize=11)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "onboarding_vs_churn.png", dpi=300)
    plt.close()

    # 5. Feature Usage Distribution
    logger.info("Analyzing feature usage distribution...")
    feature_counts = activity["feature_name"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(feature_counts.index, feature_counts.values, color="#1abc9c")
    for bar in bars:
        w = bar.get_width()
        ax.text(w + 10000, bar.get_y() + bar.get_height() / 2, f"{w:,} ({w/len(activity):.1%})",
                ha="left", va="center", fontsize=9, fontweight="bold")
    ax.set_title("Application Feature Interaction Breakdown (Total Events)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xlabel("Total Event Count", fontsize=11)
    ax.set_xlim(0, max(feature_counts.values) * 1.25)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "feature_usage_distribution.png", dpi=300)
    plt.close()

    # 6. Revenue Breakdown by Subscription Plan & Product Type
    logger.info("Analyzing revenue breakdown...")
    success_txns = txns[txns["payment_status"] == "Success"].copy()
    rev_by_product = success_txns.groupby("product_type")["amount"].agg(["count", "sum"]).reset_index()
    rev_by_product.columns = ["product_type", "transactions_count", "total_revenue"]
    rev_by_product = rev_by_product.sort_values("total_revenue", ascending=False)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(rev_by_product["product_type"], rev_by_product["total_revenue"], color="#2c3e50", width=0.55)
    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 2000, f"${h:,.0f}", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.set_title("Total Realized Revenue by Product & Subscription Type", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Gross Realized Revenue ($)", fontsize=11)
    ax.set_xticklabels(rev_by_product["product_type"], rotation=25, ha="right")
    ax.set_ylim(0, max(rev_by_product["total_revenue"]) * 1.15)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "revenue_by_plan.png", dpi=300)
    plt.close()

    # 7. Customer Tenure vs. Churn Rate
    logger.info("Analyzing tenure vs churn...")
    user_master["signup_dt"] = pd.to_datetime(user_master["signup_date"])
    cutoff_dt = pd.to_datetime("2025-08-31")
    user_master["tenure_days"] = (cutoff_dt - user_master["signup_dt"]).dt.days
    user_master["tenure_bucket"] = pd.cut(
        user_master["tenure_days"],
        bins=[30, 60, 90, 120, 150, 250],
        labels=["31-60 days", "61-90 days", "91-120 days", "121-150 days", "150+ days"]
    )
    tenure_summary = user_master.groupby("tenure_bucket", observed=False)["churn_label"].agg(["count", "mean"]).reset_index()

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(tenure_summary["tenure_bucket"].astype(str), tenure_summary["mean"] * 100, marker="o", color="#d35400", linewidth=2.5, markersize=8)
    for i, row in tenure_summary.iterrows():
        ax.text(i, row["mean"] * 100 + 1.2, f"{row['mean']*100:.1f}%", ha="center", fontweight="bold")
    ax.set_title("Customer Churn Rate by Tenure Bucket (at Cutoff)", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Churn Rate (%)", fontsize=11)
    ax.set_xlabel("Tenure Bucket (Days Since Registration)", fontsize=11)
    ax.set_ylim(0, 100)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "tenure_vs_churn.png", dpi=300)
    plt.close()

    # 8. Behavioral Decay Leading up to Cutoff (Days 30 to 0 before Cutoff)
    logger.info("Analyzing session decay prior to cutoff...")
    act_filtered = activity[activity["event_date"] <= "2025-08-31"].copy()
    act_filtered["event_dt"] = pd.to_datetime(act_filtered["event_date"])
    act_filtered["days_before_cutoff"] = (cutoff_dt - act_filtered["event_dt"]).dt.days

    # Filter to last 30 days before cutoff
    recent_act = act_filtered[act_filtered["days_before_cutoff"] <= 30].copy()
    recent_act = recent_act.merge(churn[["user_id", "churn_label"]], on="user_id")

    # Group into 5-day windows
    recent_act["window_group"] = pd.cut(
        recent_act["days_before_cutoff"],
        bins=[-1, 5, 10, 15, 20, 25, 30],
        labels=["0-5 days", "6-10 days", "11-15 days", "16-20 days", "21-25 days", "26-30 days"]
    )
    decay_series = recent_act.groupby(["window_group", "churn_label"], observed=False)["event_id"].count().unstack()
    # Normalize by user count in each group
    retained_users_count = (churn["churn_label"] == 0).sum()
    churned_users_count = (churn["churn_label"] == 1).sum()
    decay_series[0] = decay_series[0] / retained_users_count
    decay_series[1] = decay_series[1] / churned_users_count

    fig, ax = plt.subplots(figsize=(9, 5))
    x_labels = list(reversed(decay_series.index.astype(str)))
    y_ret = list(reversed(decay_series[0].values))
    y_chu = list(reversed(decay_series[1].values))

    ax.plot(x_labels, y_ret, marker="s", color="#27ae60", label="Retained Users (Events/User)", linewidth=2.5)
    ax.plot(x_labels, y_chu, marker="^", color="#c0392b", label="Churned Users (Events/User)", linewidth=2.5)
    ax.set_title("Behavioral Telemetry Decay in Final 30 Days Prior to Cutoff", fontsize=13, fontweight="bold", pad=15)
    ax.set_ylabel("Avg Events per User", fontsize=11)
    ax.set_xlabel("Observation Window Countdown (Days to Cutoff)", fontsize=11)
    ax.legend(loc="upper right", frameon=True)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "engagement_decay_pre_churn.png", dpi=300)
    plt.close()

    logger.info("All 8 publication-ready figures generated in %s", FIGURES_DIR)

    # Print summary metrics for verification
    print("\n" + "=" * 60)
    print("ASTROGUIDE AI - SUMMARY EDA METRICS")
    print("=" * 60)
    print(f"Total Users:             {len(user_master):,}")
    print(f"Overall Churn Rate:      {churn_rate:.2%}")
    print(f"Onboarded Churn Rate:    {onboard_summary.loc[onboard_summary['onboarding_completed']==True, 'mean'].values[0]:.2%}")
    print(f"Non-Onboarded Churn:     {onboard_summary.loc[onboard_summary['onboarding_completed']==False, 'mean'].values[0]:.2%}")
    print(f"Weekly Plan Churn:       {plan_summary.loc[plan_summary['subscription_plan']=='Weekly_Premium', 'churn_rate'].values[0]:.2%}")
    print(f"Annual Plan Churn:       {plan_summary.loc[plan_summary['subscription_plan']=='Annual_Premium', 'churn_rate'].values[0]:.2%}")
    print(f"Free Plan Churn:         {plan_summary.loc[plan_summary['subscription_plan']=='Free', 'churn_rate'].values[0]:.2%}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_eda()
