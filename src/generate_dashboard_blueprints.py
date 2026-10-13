"""
AstroGuide AI - Power BI Visual Blueprint & Blueprint Generator
==============================================================
Generates publication-quality visual blueprints of the 3-page Power BI dashboard
based on verified Star Schema tables and model predictions.
Exports blueprints to powerbi/screenshots/ for portfolio documentation.

Author: AstroGuide Analytics Team
"""

import logging
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import pandas as pd

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SCREENSHOTS_DIR = Path("powerbi/screenshots")
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR = Path("data/processed")

# Set theme styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.sans-serif"] = "Helvetica", "Arial", "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#CBD5E1"
plt.rcParams["axes.linewidth"] = 0.8


def load_star_schema():
    dim_user = pd.read_csv(DATA_DIR / "DimUser.csv")
    dim_plan = pd.read_csv(DATA_DIR / "DimPlan.csv")
    dim_date = pd.read_csv(DATA_DIR / "DimDate.csv")
    fact_txns = pd.read_csv(DATA_DIR / "FactTransactions.csv")
    fact_act = pd.read_csv(DATA_DIR / "FactActivity.csv")
    fact_churn = pd.read_csv(DATA_DIR / "fact_churn_prediction.csv")
    return dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn


def draw_card(ax, title, value, subtext="", bg_color="#F8FAFC", border_color="#E2E8F0"):
    """Render a clean Power BI KPI Card visual."""
    ax.set_facecolor(bg_color)
    for spine in ax.spines.values():
        spine.set_color(border_color)
        spine.set_linewidth(1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.72, title.upper(), ha="center", va="center", fontsize=8.5, fontweight="bold", color="#64748B", transform=ax.transAxes)
    ax.text(0.5, 0.42, value, ha="center", va="center", fontsize=15, fontweight="heavy", color="#0F172A", transform=ax.transAxes)
    if subtext:
        ax.text(0.5, 0.18, subtext, ha="center", va="center", fontsize=7.5, color="#059669" if "57.0%" in subtext or "Lowest" in subtext else "#DC2626" if "42.9%" in subtext or "Risk" in subtext else "#475569", transform=ax.transAxes)


def render_page1_executive_overview(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn):
    """Render Page 1: Executive Overview Dashboard Blueprint."""
    logger.info("Rendering Page 1: Executive Overview...")
    fig = plt.figure(figsize=(16, 9), facecolor="#F1F5F9")
    gs = gridspec.GridSpec(4, 4, figure=fig, height_ratios=[0.5, 0.8, 2.0, 2.0], hspace=0.35, wspace=0.25,
                           top=0.95, bottom=0.06, left=0.05, right=0.95)

    # 1. Header Banner
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.set_facecolor("#1E293B")
    for spine in ax_head.spines.values(): spine.set_visible(False)
    ax_head.set_xticks([]); ax_head.set_yticks([])
    ax_head.text(0.02, 0.5, "ASTROGUIDE AI  |  EXECUTIVE OVERVIEW & RETENTION COHORTS",
                 color="#FFFFFF", fontsize=13, fontweight="bold", va="center")
    ax_head.text(0.98, 0.5, "SLICERS: Plan [All]  |  Channel [All]  |  Device [All]  |  Evaluation: Aug-Sep 2025",
                 color="#94A3B8", fontsize=8.5, va="center", ha="right")

    # 2. KPI Cards
    ax_kpi1 = fig.add_subplot(gs[1, 0])
    draw_card(ax_kpi1, "Total Registered Users", "10,000", "7-Month Acquisition Cohort")

    ax_kpi2 = fig.add_subplot(gs[1, 1])
    draw_card(ax_kpi2, "Net Realized Revenue", "$192,164", "Gross: $194.4k | Refunds: $2.2k")

    ax_kpi3 = fig.add_subplot(gs[1, 2])
    draw_card(ax_kpi3, "Cohort Churn Rate", "42.98%", "4,298 Users Inactive in 30d Window")

    ax_kpi4 = fig.add_subplot(gs[1, 3])
    draw_card(ax_kpi4, "Paying Users & ARPPU", "5,745", "ARPPU: $33.45 | Blended: $19.22")

    # 3. Monthly Revenue Trend (Column & Line)
    ax_chart1 = fig.add_subplot(gs[2, :2])
    success_txns = fact_txns[fact_txns["payment_status"] == "Success"].copy()
    success_txns["month"] = pd.to_datetime(success_txns["transaction_date"]).dt.strftime("%b %Y")
    rev_trend = success_txns.groupby("month", sort=False)["amount"].sum()
    months = list(rev_trend.index)
    amounts = list(rev_trend.values)

    bars = ax_chart1.bar(months, [a/1000 for a in amounts], color="#3B82F6", width=0.55, label="Net Revenue ($k)")
    ax_chart1.set_title("Monthly Realized Revenue Performance ($ in Thousands)", fontsize=10, fontweight="bold", pad=8)
    ax_chart1.set_ylabel("Revenue ($k)", fontsize=8.5)
    ax_chart1.set_ylim(0, max(amounts)/1000 * 1.25)
    for b in bars:
        h = b.get_height()
        ax_chart1.text(b.get_x() + b.get_width()/2, h + 0.5, f"${h:.1f}k", ha="center", va="bottom", fontsize=7.5, fontweight="bold")
    ax_chart1.tick_params(axis="x", rotation=25, labelsize=8)

    # 4. Churn Rate by Acquisition Channel
    ax_chart2 = fig.add_subplot(gs[2, 2:])
    user_churn = dim_user.merge(fact_churn[["user_id", "churn_label"]], on="user_id")
    chan_churn = user_churn.groupby("acquisition_channel")["churn_label"].agg(["count", "mean"]).reset_index()
    chan_churn = chan_churn.sort_values("mean", ascending=True)

    y_pos = np.arange(len(chan_churn))
    ax_chart2.barh(y_pos, chan_churn["mean"] * 100, color=["#10B981" if x < 0.40 else "#EF4444" for x in chan_churn["mean"]], height=0.55)
    ax_chart2.set_yticks(y_pos)
    ax_chart2.set_yticklabels(chan_churn["acquisition_channel"], fontsize=8.5)
    ax_chart2.set_title("Customer Churn Rate by Acquisition Channel (%)", fontsize=10, fontweight="bold", pad=8)
    ax_chart2.set_xlabel("Churn Rate (%)", fontsize=8.5)
    ax_chart2.set_xlim(0, 55)
    for i, v in enumerate(chan_churn["mean"] * 100):
        ax_chart2.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=8, fontweight="bold")

    # 5. Plan Breakdown & Churn
    ax_chart3 = fig.add_subplot(gs[3, :2])
    plan_churn = user_churn.groupby("initial_plan")["churn_label"].agg(["count", "mean"]).reindex(
        ["Annual_Premium", "Monthly_Premium", "Free", "Weekly_Premium"]
    ).reset_index()

    bars3 = ax_chart3.bar(plan_churn["initial_plan"], plan_churn["mean"] * 100,
                          color=["#10B981", "#3B82F6", "#64748B", "#EF4444"], width=0.5)
    ax_chart3.set_title("Churn Rate by Initial Subscription Plan Tier (%)", fontsize=10, fontweight="bold", pad=8)
    ax_chart3.set_ylabel("Churn Rate (%)", fontsize=8.5)
    ax_chart3.set_ylim(0, 65)
    for b in bars3:
        h = b.get_height()
        ax_chart3.text(b.get_x() + b.get_width()/2, h + 1.2, f"{h:.1f}%", ha="center", fontsize=8, fontweight="bold")
    ax_chart3.tick_params(axis="x", rotation=15, labelsize=8)

    # 6. Executive Key Findings Callout Table
    ax_callout = fig.add_subplot(gs[3, 2:])
    ax_callout.set_facecolor("#FFFFFF")
    for spine in ax_callout.spines.values(): spine.set_color("#CBD5E1")
    ax_callout.set_xticks([]); ax_callout.set_yticks([])
    ax_callout.text(0.04, 0.88, "EXECUTIVE SUMMARY & BUSINESS TAKEAWAYS", fontsize=9.5, fontweight="bold", color="#0F172A")
    bullets = [
        "• Annual Subscribers exhibit best retention (30.98% churn, 69.02% retention).",
        "• Weekly Subscribers experience severe churn (52.16%) driven by frequent renewal friction.",
        "• Paid social campaigns (TikTok: 45.5%, IG: 44.7%) require onboarding optimization.",
        "• Referral & Organic channels yield highest LTV with lowest acquisition churn (~39%).",
        "• 5,745 paying users generated $192.1k net revenue ($33.45 ARPPU)."
    ]
    for i, b in enumerate(bullets):
        ax_callout.text(0.04, 0.70 - (i * 0.14), b, fontsize=8, color="#334155")

    fig.savefig(SCREENSHOTS_DIR / "page1_executive_overview.png", dpi=300)
    plt.close()
    logger.info("Saved Page 1 blueprint to %s", SCREENSHOTS_DIR / "page1_executive_overview.png")


def render_page2_engagement_diagnostics(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn):
    """Render Page 2: Engagement & Retention Diagnostics."""
    logger.info("Rendering Page 2: Engagement & Retention Diagnostics...")
    fig = plt.figure(figsize=(16, 9), facecolor="#F1F5F9")
    gs = gridspec.GridSpec(4, 4, figure=fig, height_ratios=[0.5, 0.8, 2.0, 2.0], hspace=0.35, wspace=0.25,
                           top=0.95, bottom=0.06, left=0.05, right=0.95)

    # Header
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.set_facecolor("#1E293B")
    for spine in ax_head.spines.values(): spine.set_visible(False)
    ax_head.set_xticks([]); ax_head.set_yticks([])
    ax_head.text(0.02, 0.5, "ASTROGUIDE AI  |  ENGAGEMENT & RETENTION DIAGNOSTICS",
                 color="#FFFFFF", fontsize=13, fontweight="bold", va="center")
    ax_head.text(0.98, 0.5, "SLICERS: Onboarding [All]  |  Plan [All]  |  Age [All]  |  Telemetry: 1.35M Events",
                 color="#94A3B8", fontsize=8.5, va="center", ha="right")

    # KPI Cards
    ax_kpi1 = fig.add_subplot(gs[1, 0])
    draw_card(ax_kpi1, "Onboarding Completion Rate", "69.07%", "6,907 Activated Users")

    ax_kpi2 = fig.add_subplot(gs[1, 1])
    draw_card(ax_kpi2, "Onboarded vs Drop Churn", "32.0% vs 67.4%", "2.1x Higher Risk on Drop-off")

    ax_kpi3 = fig.add_subplot(gs[1, 2])
    draw_card(ax_kpi3, "Total Telemetry Events", "1,345,770", "Avg 134.6 Events / User")

    ax_kpi4 = fig.add_subplot(gs[1, 3])
    draw_card(ax_kpi4, "Avg Session Duration", "1.68 min", "Avg 101 Seconds / Event")

    # 1. Onboarding vs Churn
    ax_chart1 = fig.add_subplot(gs[2, :2])
    user_churn = dim_user.merge(fact_churn[["user_id", "churn_label"]], on="user_id")
    onboard_stat = user_churn.groupby("onboarding_completed")["churn_label"].mean() * 100
    bars = ax_chart1.bar(["Completed Onboarding", "Dropped Off Onboarding"],
                         [onboard_stat["Completed"], onboard_stat["Dropped Off"]],
                         color=["#10B981", "#EF4444"], width=0.45)
    ax_chart1.set_title("Onboarding Completion vs. Churn Rate (%)", fontsize=10, fontweight="bold", pad=8)
    ax_chart1.set_ylabel("Churn Rate (%)", fontsize=8.5)
    ax_chart1.set_ylim(0, 80)
    for b in bars:
        h = b.get_height()
        ax_chart1.text(b.get_x() + b.get_width()/2, h + 1.5, f"{h:.1f}%", ha="center", fontsize=8.5, fontweight="bold")

    # 2. Feature Engagement Share
    ax_chart2 = fig.add_subplot(gs[2, 2:])
    feat_counts = fact_act["feature_name"].value_counts().sort_values(ascending=True)
    y_pos = np.arange(len(feat_counts))
    ax_chart2.barh(y_pos, feat_counts.values / 1000, color="#6366F1", height=0.55)
    ax_chart2.set_yticks(y_pos)
    ax_chart2.set_yticklabels(feat_counts.index, fontsize=8.5)
    ax_chart2.set_title("Feature Telemetry Interaction Volume (Events in Thousands)", fontsize=10, fontweight="bold", pad=8)
    ax_chart2.set_xlabel("Events (Thousands)", fontsize=8.5)
    for i, v in enumerate(feat_counts.values / 1000):
        ax_chart2.text(v + 5, i, f"{v:.1f}k ({v/len(fact_act)*1000:.1f}%)", va="center", fontsize=8, fontweight="bold")

    # 3. 30-Day Pre-Cutoff Session Decay Curve
    ax_chart3 = fig.add_subplot(gs[3, :2])
    act_pre = fact_act[fact_act["event_date"] <= "2025-08-31"].copy()
    act_pre["days_to_cutoff"] = (pd.to_datetime("2025-08-31") - pd.to_datetime(act_pre["event_date"])).dt.days
    recent_act = act_pre[act_pre["days_to_cutoff"] <= 30].merge(fact_churn[["user_id", "churn_label"]], on="user_id")

    # Group into 5-day intervals
    recent_act["window_group"] = pd.cut(recent_act["days_to_cutoff"], bins=[-1, 5, 10, 15, 20, 25, 30],
                                        labels=["0-5d", "6-10d", "11-15d", "16-20d", "21-25d", "26-30d"])
    decay = recent_act.groupby(["window_group", "churn_label"], observed=False)["event_id"].count().unstack()
    decay[0] = decay[0] / 5702
    decay[1] = decay[1] / 4298

    x_labels = list(reversed(decay.index.astype(str)))
    ax_chart3.plot(x_labels, list(reversed(decay[0].values)), marker="s", color="#10B981", label="Retained Cohort", linewidth=2.2)
    ax_chart3.plot(x_labels, list(reversed(decay[1].values)), marker="^", color="#EF4444", label="Churned Cohort", linewidth=2.2)
    ax_chart3.set_title("Behavioral Telemetry Decay (Events/User in 30 Days Preceding Cutoff)", fontsize=10, fontweight="bold", pad=8)
    ax_chart3.set_ylabel("Events per User", fontsize=8.5)
    ax_chart3.set_xlabel("Countdown to Cutoff Date", fontsize=8.5)
    ax_chart3.legend(fontsize=8, loc="upper right")

    # 4. Cohort Retention Triangle Matrix (Table representation)
    ax_chart4 = fig.add_subplot(gs[3, 2:])
    ax_chart4.set_facecolor("#FFFFFF")
    for spine in ax_chart4.spines.values(): spine.set_color("#CBD5E1")
    ax_chart4.set_xticks([]); ax_chart4.set_yticks([])
    ax_chart4.text(0.04, 0.90, "MONTHLY SIGNUP COHORT RETENTION MATRIX (%)", fontsize=9.5, fontweight="bold", color="#0F172A")

    matrix_rows = [
        "Cohort       Users     M0       M1       M2       M3       M4       M5       M6",
        "--------------------------------------------------------------------------------",
        "2025-01     1,453   87.9%   89.3%   75.3%   62.8%   57.7%   55.1%   52.0%",
        "2025-02     1,355   86.5%   91.1%   74.7%   64.5%   59.3%   55.6%   52.6%",
        "2025-03     1,459   87.5%   88.5%   75.5%   63.0%   58.5%   54.6%     -",
        "2025-04     1,506   87.6%   90.0%   74.9%   65.1%   59.4%     -       -",
        "2025-05     1,390   87.2%   89.0%   72.9%   64.0%     -       -       -",
        "2025-06     1,425   88.7%   90.2%   73.8%     -       -       -       -",
        "2025-07     1,412   88.0%   89.0%     -       -       -       -       -"
    ]
    for i, row in enumerate(matrix_rows):
        ax_chart4.text(0.04, 0.78 - (i * 0.08), row, fontsize=7.5, fontfamily="monospace",
                       color="#0F172A" if i < 2 else "#334155", fontweight="bold" if i < 2 else "normal")

    fig.savefig(SCREENSHOTS_DIR / "page2_engagement_retention.png", dpi=300)
    plt.close()
    logger.info("Saved Page 2 blueprint to %s", SCREENSHOTS_DIR / "page2_engagement_retention.png")


def render_page3_churn_risk_actions(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn):
    """Render Page 3: Churn Risk & Actionable Interventions."""
    logger.info("Rendering Page 3: Churn Risk & Actions...")
    fig = plt.figure(figsize=(16, 9), facecolor="#F1F5F9")
    gs = gridspec.GridSpec(4, 4, figure=fig, height_ratios=[0.5, 0.8, 2.0, 2.0], hspace=0.35, wspace=0.25,
                           top=0.95, bottom=0.06, left=0.05, right=0.95)

    # Header
    ax_head = fig.add_subplot(gs[0, :])
    ax_head.set_facecolor("#1E293B")
    for spine in ax_head.spines.values(): spine.set_visible(False)
    ax_head.set_xticks([]); ax_head.set_yticks([])
    ax_head.text(0.02, 0.5, "ASTROGUIDE AI  |  PREDICTIVE CHURN RISK & RETENTION ACTIONS",
                 color="#FFFFFF", fontsize=13, fontweight="bold", va="center")
    ax_head.text(0.98, 0.5, "ML INFERENCE: Logistic Regression (Balanced)  |  ROC-AUC: 0.9294  |  Recall: 83.14%",
                 color="#94A3B8", fontsize=8.5, va="center", ha="right")

    # KPI Cards
    ax_kpi1 = fig.add_subplot(gs[1, 0])
    draw_card(ax_kpi1, "At-Risk Customers (High)", "3,520", "35.20% of Customer Base")

    ax_kpi2 = fig.add_subplot(gs[1, 1])
    draw_card(ax_kpi2, "At-Risk Revenue Exposure", "$58,515", "30.4% of Total Net Revenue")

    ax_kpi3 = fig.add_subplot(gs[1, 2])
    draw_card(ax_kpi3, "Model ROC-AUC Score", "0.9294", "Recall: 83.1% | Precision: 79.8%")

    ax_kpi4 = fig.add_subplot(gs[1, 3])
    draw_card(ax_kpi4, "Active Warning Window", "15 Days", "Intervene Before Day 5 Cliff")

    # 1. Customer Risk Distribution (Donut Chart)
    ax_chart1 = fig.add_subplot(gs[2, :2])
    risk_counts = fact_churn["risk_tier"].value_counts().reindex(["Low Risk (<40%)", "Medium Risk (40-69%)", "High Risk (>=70%)"])
    colors = ["#10B981", "#F59E0B", "#EF4444"]
    wedges, texts, autotexts = ax_chart1.pie(risk_counts.values, labels=risk_counts.index, autopct="%1.1f%%",
                                             startangle=140, colors=colors, textprops=dict(fontsize=8.5))
    for at in autotexts: at.set_fontsize(8.5); at.set_fontweight("bold")
    ax_chart1.set_title("Predicted Customer Churn Risk Segmentation", fontsize=10, fontweight="bold", pad=8)

    # 2. At-Risk Revenue by Subscription Plan
    ax_chart2 = fig.add_subplot(gs[2, 2:])
    high_risk_users = set(fact_churn[fact_churn["risk_tier"] == "High Risk (>=70%)"]["user_id"])
    hr_txns = fact_txns[fact_txns["user_id"].isin(high_risk_users) & (fact_txns["payment_status"] == "Success")]
    hr_txns = hr_txns.merge(dim_user[["user_id", "initial_plan"]], on="user_id")
    plan_exposure = hr_txns.groupby("initial_plan")["amount"].sum().sort_values(ascending=False)

    bars2 = ax_chart2.bar(plan_exposure.index, plan_exposure.values / 1000, color="#EC4899", width=0.5)
    ax_chart2.set_title("At-Risk Net Revenue Exposure by Subscription Plan ($k)", fontsize=10, fontweight="bold", pad=8)
    ax_chart2.set_ylabel("Revenue at Risk ($k)", fontsize=8.5)
    ax_chart2.set_ylim(0, max(plan_exposure.values)/1000 * 1.25)
    for b in bars2:
        h = b.get_height()
        ax_chart2.text(b.get_x() + b.get_width()/2, h + 0.4, f"${h:.1f}k", ha="center", fontsize=8, fontweight="bold")
    ax_chart2.tick_params(axis="x", rotation=15, labelsize=8)

    # 3. Recency vs Churn Probability Scatter
    ax_chart3 = fig.add_subplot(gs[3, :2])
    sample_churn = fact_churn.sample(n=600, random_state=42)
    sc = ax_chart3.scatter(sample_churn["days_since_last_session"], sample_churn["churn_probability"],
                           c=sample_churn["churn_probability"], cmap="RdYlGn_r", alpha=0.6, s=18)
    ax_chart3.set_title("Churn Probability vs. Days Since Last Active Session (Recency)", fontsize=10, fontweight="bold", pad=8)
    ax_chart3.set_xlabel("Days Since Last Active Session (at Cutoff)", fontsize=8.5)
    ax_chart3.set_ylabel("Model Churn Probability", fontsize=8.5)
    ax_chart3.axhline(0.70, color="#EF4444", linestyle="--", linewidth=1.2, label="High Risk Threshold (>=70%)")
    ax_chart3.legend(fontsize=8, loc="lower right")

    # 4. Actionable Retention Interventions Table
    ax_table = fig.add_subplot(gs[3, 2:])
    ax_table.set_facecolor("#FFFFFF")
    for spine in ax_table.spines.values(): spine.set_color("#CBD5E1")
    ax_table.set_xticks([]); ax_table.set_yticks([])
    ax_table.text(0.04, 0.90, "RECOMMENDED RETENTION ACTIONS BY SEGMENT", fontsize=9.5, fontweight="bold", color="#0F172A")

    actions = [
        "1. High-Risk Weekly Subs ($17.5k at risk): Test 20% discount offer to convert to Monthly plan.",
        "2. Dropped-Off Onboarding (67.4% churn): Trigger automated 'Complete Your Birth Chart' push on Day 2.",
        "3. Inactivity Gap >= 7 Days: Send personalized astrological transit notification ('Mars enters Scorpio').",
        "4. Single-Feature Users: In-app prompt offering 1 Free AI Astrology Chat session upon login.",
        "5. Annual Subscribers (Lowest Churn): Deliver VIP loyalty perks and early access to yearly forecasts."
    ]
    for i, act in enumerate(actions):
        ax_table.text(0.04, 0.74 - (i * 0.15), act, fontsize=7.8, color="#334155")

    fig.savefig(SCREENSHOTS_DIR / "page3_churn_risk_actions.png", dpi=300)
    plt.close()
    logger.info("Saved Page 3 blueprint to %s", SCREENSHOTS_DIR / "page3_churn_risk_actions.png")


def main():
    dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn = load_star_schema()
    render_page1_executive_overview(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn)
    render_page2_engagement_diagnostics(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn)
    render_page3_churn_risk_actions(dim_user, dim_plan, dim_date, fact_txns, fact_act, fact_churn)
    logger.info("All 3 Power BI visual blueprints successfully generated in %s!", SCREENSHOTS_DIR)


if __name__ == "__main__":
    main()
