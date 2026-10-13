"""
AstroGuide AI - Synthetic Relational Data Generator
===================================================
Generates a realistic multi-table relational dataset for customer churn and
retention analytics, modeling user signups, activity telemetry, subscription
lifecycles, financial transactions, and leakage-aware churn labels.

Author: AstroGuide Analytics Team
Seed: 42 (Reproducible)
"""

import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def generate_users(
    n_users: int,
    start_date: datetime,
    end_date: datetime,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Generate synthetic users table.

    Parameters:
    -----------
    n_users : int
        Number of synthetic users to generate.
    start_date : datetime
        Earliest possible signup date.
    end_date : datetime
        Latest possible signup date.
    rng : np.random.Generator
        Configured NumPy random generator.

    Returns:
    --------
    pd.DataFrame
        Users table with demographics, acquisition, and onboarding details.
    """
    logger.info("Generating %d synthetic users...", n_users)

    user_ids = [f"USR_{i:06d}" for i in range(1, n_users + 1)]

    # Signup dates uniformly distributed across the acquisition window
    total_days = (end_date - start_date).days
    random_days = rng.integers(0, total_days + 1, size=n_users)
    signup_dates = [
        (start_date + timedelta(days=int(d))).strftime("%Y-%m-%d")
        for d in random_days
    ]

    channels = ["Organic Search", "Instagram Ads", "TikTok Ads", "Google Ads", "Referral"]
    channel_probs = [0.25, 0.30, 0.20, 0.15, 0.10]
    acquisition_channel = rng.choice(channels, size=n_users, p=channel_probs)

    countries = ["US", "UK", "CA", "AU", "DE", "IN"]
    country_probs = [0.45, 0.15, 0.12, 0.08, 0.08, 0.12]
    country = rng.choice(countries, size=n_users, p=country_probs)

    age_groups = ["18-24", "25-34", "35-44", "45-54", "55+"]
    age_probs = [0.28, 0.38, 0.20, 0.10, 0.04]
    age_group = rng.choice(age_groups, size=n_users, p=age_probs)

    devices = ["iOS", "Android", "Web"]
    device_probs = [0.62, 0.32, 0.06]
    device_type = rng.choice(devices, size=n_users, p=device_probs)

    # Marketing campaigns mapped to acquisition channels
    campaign_map = {
        "Instagram Ads": ["IG_Summer_Vibes", "IG_Zodiac_Match", "IG_Influencer_Reel"],
        "TikTok Ads": ["TT_BirthChart_Viral", "TT_Tarot_Reveal", "TT_Astrology_Trend"],
        "Google Ads": ["GGL_Search_Horoscope", "GGL_AI_Astrologer", "GGL_Brand_Core"],
        "Organic Search": ["Organic_Direct", "SEO_Daily_Horoscope", "AppStore_Explore"],
        "Referral": ["Refer_Friend_Bonus", "Social_Share_Invite"],
    }
    marketing_campaign = [
        rng.choice(campaign_map[ch]) for ch in acquisition_channel
    ]

    zodiac_signs = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]
    zodiac_sign = rng.choice(zodiac_signs, size=n_users)

    # Onboarding completion: Influenced by age and channel
    # Younger and organic users have slightly higher onboarding rates
    base_onboarding_prob = np.where(
        np.isin(acquisition_channel, ["Organic Search", "Referral"]),
        0.78,
        0.65,
    )
    onboarding_completed = rng.random(size=n_users) < base_onboarding_prob

    # Initial plan chosen at signup
    plans = ["Free", "Weekly_Premium", "Monthly_Premium", "Annual_Premium"]
    plan_probs = [0.60, 0.18, 0.16, 0.06]
    initial_plan = rng.choice(plans, size=n_users, p=plan_probs)

    users_df = pd.DataFrame({
        "user_id": user_ids,
        "signup_date": signup_dates,
        "acquisition_channel": acquisition_channel,
        "country": country,
        "age_group": age_group,
        "device_type": device_type,
        "marketing_campaign": marketing_campaign,
        "onboarding_completed": onboarding_completed,
        "zodiac_sign": zodiac_sign,
        "subscription_plan": initial_plan,
    })

    return users_df


def generate_subscriptions(
    users_df: pd.DataFrame,
    cutoff_date: datetime,
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """
    Generate subscription history for users.

    Parameters:
    -----------
    users_df : pd.DataFrame
        Users table.
    cutoff_date : datetime
        Observation cutoff date.
    rng : np.random.Generator
        Random number generator.

    Returns:
    --------
    Tuple[pd.DataFrame, Dict[str, str]]
        Subscriptions DataFrame and mapping of user_id to subscription status at cutoff.
    """
    logger.info("Generating subscription records...")

    subscriptions = []
    sub_counter = 1
    user_status_at_cutoff = {}

    plans_info = {
        "Weekly_Premium": {"interval": "Weekly", "days": 7, "price": 3.99},
        "Monthly_Premium": {"interval": "Monthly", "days": 30, "price": 9.99},
        "Annual_Premium": {"interval": "Annual", "days": 365, "price": 59.99},
    }

    cancellation_reasons = [
        "Too Expensive",
        "Not Enough Value",
        "Technical Issues",
        "Found Alternative",
        "Infrequent Use",
    ]

    for _, row in users_df.iterrows():
        u_id = row["user_id"]
        init_plan = row["subscription_plan"]
        signup_dt = datetime.strptime(row["signup_date"], "%Y-%m-%d")

        if init_plan == "Free":
            # Some free users upgrade later
            will_upgrade = rng.random() < 0.12
            if not will_upgrade:
                user_status_at_cutoff[u_id] = "Free"
                continue
            plan = rng.choice(["Weekly_Premium", "Monthly_Premium"], p=[0.55, 0.45])
            start_dt = signup_dt + timedelta(days=int(rng.integers(1, 21)))
        else:
            plan = init_plan
            start_dt = signup_dt

        plan_meta = plans_info[plan]
        plan_days = plan_meta["days"]

        # Determine renewals and cancellation
        # Annual subscribers renew more and cancel less
        if plan == "Annual_Premium":
            prob_cancel = 0.20
            max_renewals = 2
        elif plan == "Monthly_Premium":
            prob_cancel = 0.45
            max_renewals = 6
        else:  # Weekly
            prob_cancel = 0.65
            max_renewals = 12

        # Non-onboarded users cancel at higher rates
        if not row["onboarding_completed"]:
            prob_cancel = min(0.90, prob_cancel + 0.20)

        cancels = rng.random() < prob_cancel

        if cancels:
            renewals = int(rng.geometric(p=0.45) - 1)
            renewals = min(renewals, max_renewals)
            duration_days = (renewals + 1) * plan_days
            cancel_dt = start_dt + timedelta(days=duration_days)
            end_dt = cancel_dt
            status = "Cancelled"
            reason = rng.choice(cancellation_reasons)
        else:
            # Active subscription: renewed up to or past cutoff
            days_since_start = max(0, (cutoff_date - start_dt).days)
            renewals = max(0, days_since_start // plan_days)
            cancel_dt = None
            end_dt = start_dt + timedelta(days=int((renewals + 1) * plan_days))
            status = "Active"
            reason = "None"

        sub_id = f"SUB_{sub_counter:06d}"
        sub_counter += 1

        subscriptions.append({
            "subscription_id": sub_id,
            "user_id": u_id,
            "plan_name": plan,
            "subscription_start_date": start_dt.strftime("%Y-%m-%d"),
            "subscription_end_date": end_dt.strftime("%Y-%m-%d"),
            "billing_interval": plan_meta["interval"],
            "subscription_status": status,
            "renewal_count": renewals,
            "cancellation_date": cancel_dt.strftime("%Y-%m-%d") if cancel_dt else None,
            "cancellation_reason": reason,
        })

        user_status_at_cutoff[u_id] = status

    subs_df = pd.DataFrame(subscriptions)
    return subs_df, user_status_at_cutoff


def generate_transactions(
    subs_df: pd.DataFrame,
    users_df: pd.DataFrame,
    cutoff_date: datetime,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Generate transactions including subscription renewals, one-off purchases,
    failed payments, and refunds.

    Parameters:
    -----------
    subs_df : pd.DataFrame
        Subscriptions table.
    users_df : pd.DataFrame
        Users table.
    cutoff_date : datetime
        Cutoff date for transaction generation.
    rng : np.random.Generator
        Random generator.

    Returns:
    --------
    pd.DataFrame
        Transactions table.
    """
    logger.info("Generating transactions...")

    transactions = []
    txn_counter = 1

    plan_prices = {
        "Weekly_Premium": 3.99,
        "Monthly_Premium": 9.99,
        "Annual_Premium": 59.99,
    }
    plan_intervals = {
        "Weekly_Premium": 7,
        "Monthly_Premium": 30,
        "Annual_Premium": 365,
    }

    # 1. Subscription Transactions (Initial + Renewals)
    for _, sub in subs_df.iterrows():
        u_id = sub["user_id"]
        plan = sub["plan_name"]
        price = plan_prices[plan]
        interval_days = plan_intervals[plan]
        start_dt = datetime.strptime(sub["subscription_start_date"], "%Y-%m-%d")
        renewals = sub["renewal_count"]

        # Initial payment
        t_id = f"TXN_{txn_counter:07d}"
        txn_counter += 1
        transactions.append({
            "transaction_id": t_id,
            "user_id": u_id,
            "transaction_date": start_dt.strftime("%Y-%m-%d"),
            "product_type": "Subscription_Initial",
            "amount": price,
            "currency": "USD",
            "payment_status": "Success",
            "refund_flag": False,
        })

        # Renewals
        for r in range(1, renewals + 1):
            cycle_dt = start_dt + timedelta(days=r * interval_days)
            if cycle_dt > cutoff_date:
                break

            # 3% chance of failed renewal payment
            is_failed = rng.random() < 0.03
            status = "Failed" if is_failed else "Success"
            refund = False

            if status == "Success" and rng.random() < 0.015:
                # 1.5% chance of refund
                status = "Refunded"
                refund = True

            t_id = f"TXN_{txn_counter:07d}"
            txn_counter += 1
            transactions.append({
                "transaction_id": t_id,
                "user_id": u_id,
                "transaction_date": cycle_dt.strftime("%Y-%m-%d"),
                "product_type": "Subscription_Renewal",
                "amount": price,
                "currency": "USD",
                "payment_status": status,
                "refund_flag": refund,
            })

    # 2. One-Time In-App Purchases (Tarot readings, birth chart deep dives)
    # Both free and subscribed users can purchase one-off products
    one_off_products = [
        {"name": "Tarot_Reading_OneOff", "price": 4.99},
        {"name": "Compatibility_Full_Report", "price": 7.99},
        {"name": "Yearly_Transit_Forecast", "price": 12.99},
    ]

    for _, user in users_df.iterrows():
        u_id = user["user_id"]
        signup_dt = datetime.strptime(user["signup_date"], "%Y-%m-%d")
        days_active = max(1, (cutoff_date - signup_dt).days)

        # 18% of users buy one-off reports
        if rng.random() < 0.18:
            n_purchases = rng.integers(1, 4)
            for _ in range(n_purchases):
                prod = rng.choice(one_off_products)
                buy_day = int(rng.integers(0, days_active))
                buy_dt = signup_dt + timedelta(days=buy_day)

                is_refund = rng.random() < 0.02
                status = "Refunded" if is_refund else "Success"

                t_id = f"TXN_{txn_counter:07d}"
                txn_counter += 1
                transactions.append({
                    "transaction_id": t_id,
                    "user_id": u_id,
                    "transaction_date": buy_dt.strftime("%Y-%m-%d"),
                    "product_type": prod["name"],
                    "amount": prod["price"],
                    "currency": "USD",
                    "payment_status": status,
                    "refund_flag": is_refund,
                })

    txns_df = pd.DataFrame(transactions)
    # Sort chronologically
    txns_df = txns_df.sort_values("transaction_date").reset_index(drop=True)
    return txns_df


def generate_activity_and_churn(
    users_df: pd.DataFrame,
    subs_df: pd.DataFrame,
    start_date: datetime,
    cutoff_date: datetime,
    outcome_end_date: datetime,
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Generate event telemetry stream and ground-truth churn labels.

    Leakage-Free Protocol:
    ----------------------
    - Observation Window: [signup_date, cutoff_date]
    - Outcome Window: (cutoff_date, outcome_end_date] (30 calendar days)
    - Target Label: churn_label = 1 if user has 0 sessions in the Outcome Window,
                    churn_label = 0 if user has >= 1 session in the Outcome Window.

    Parameters:
    -----------
    users_df : pd.DataFrame
        Users table.
    subs_df : pd.DataFrame
        Subscriptions table.
    start_date : datetime
        Earliest data generation date.
    cutoff_date : datetime
        The strict observation cutoff date (t_0).
    outcome_end_date : datetime
        End of outcome window (t_0 + 30 days).
    rng : np.random.Generator
        Random generator.

    Returns:
    --------
    Tuple[pd.DataFrame, pd.DataFrame]
        Activity DataFrame (all events up to outcome_end_date) and
        Churn Labels DataFrame (strictly evaluated at cutoff_date).
    """
    logger.info("Generating activity telemetry and leakage-free churn labels...")

    # Map user cancellation dates to inform behavioral decay
    cancellation_dates = {}
    for _, row in subs_df.iterrows():
        if pd.notna(row["cancellation_date"]) and row["cancellation_date"] is not None:
            cancellation_dates[row["user_id"]] = datetime.strptime(
                str(row["cancellation_date"]), "%Y-%m-%d"
            )

    events = []
    churn_records = []
    evt_counter = 1

    event_taxonomy = [
        {"type": "daily_horoscope_view", "feature": "Horoscope", "base_weight": 0.40, "avg_dur": 75},
        {"type": "ai_chat_started", "feature": "AI_Chat", "base_weight": 0.20, "avg_dur": 240},
        {"type": "compatibility_report_viewed", "feature": "Compatibility", "base_weight": 0.15, "avg_dur": 180},
        {"type": "tarot_reading_completed", "feature": "Tarot", "base_weight": 0.15, "avg_dur": 190},
        {"type": "paywall_viewed", "feature": "Paywall", "base_weight": 0.05, "avg_dur": 30},
        {"type": "notification_opened", "feature": "Notification", "base_weight": 0.05, "avg_dur": 20},
    ]
    event_weights = [t["base_weight"] for t in event_taxonomy]
    n_event_types = len(event_taxonomy)

    for _, user in users_df.iterrows():
        u_id = user["user_id"]
        signup_dt = datetime.strptime(user["signup_date"], "%Y-%m-%d")
        onboarded = user["onboarding_completed"]
        plan = user["subscription_plan"]
        is_paid = plan != "Free"

        # Determine user baseline engagement archetype
        # Highly engaged vs casual vs fading
        if is_paid and onboarded:
            archetype_probs = [0.55, 0.30, 0.15]  # [Loyal, Moderate, Fading]
        elif onboarded:
            archetype_probs = [0.25, 0.45, 0.30]
        else:
            archetype_probs = [0.08, 0.27, 0.65]

        archetype = rng.choice(["Loyal", "Moderate", "Fading"], p=archetype_probs)

        # Baseline daily activity probability
        if archetype == "Loyal":
            daily_active_prob = 0.60
            decay_factor = 0.999
        elif archetype == "Moderate":
            daily_active_prob = 0.30
            decay_factor = 0.992
        else:  # Fading
            daily_active_prob = 0.15
            decay_factor = 0.970

        cancel_dt = cancellation_dates.get(u_id)

        # Generate sessions day by day from signup to outcome_end_date
        current_dt = signup_dt
        user_session_num = 1
        sessions_in_outcome_window = 0

        while current_dt <= outcome_end_date:
            days_since_signup = (current_dt - signup_dt).days

            # Calculate day-specific active probability with realistic decay
            eff_prob = daily_active_prob * (decay_factor ** days_since_signup)

            # If user already cancelled subscription, activity drops severely
            if cancel_dt and current_dt > cancel_dt:
                eff_prob *= 0.10

            is_active_today = rng.random() < eff_prob

            if is_active_today:
                if current_dt > cutoff_date:
                    sessions_in_outcome_window += 1

                # 1 to 3 sessions per active day
                n_sessions_today = int(rng.choice([1, 2, 3], p=[0.75, 0.20, 0.05]))

                for _ in range(n_sessions_today):
                    # Each session has 1 to 4 events
                    n_events_in_session = int(rng.integers(1, 5))
                    session_time_offset = int(rng.integers(0, 86400))
                    session_timestamp = current_dt + timedelta(seconds=session_time_offset)

                    # Always start session with app_open
                    e_id = f"EVT_{evt_counter:08d}"
                    evt_counter += 1
                    events.append({
                        "event_id": e_id,
                        "user_id": u_id,
                        "event_timestamp": session_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                        "event_date": session_timestamp.strftime("%Y-%m-%d"),
                        "event_type": "app_open",
                        "feature_name": "App",
                        "session_duration_seconds": 15,
                        "notification_opened": rng.random() < 0.25,
                        "session_number": user_session_num,
                    })

                    # Subsequent feature events
                    for _ in range(n_events_in_session):
                        chosen_evt = event_taxonomy[rng.choice(n_event_types, p=event_weights)]
                        dur = max(
                            10,
                            int(rng.normal(loc=chosen_evt["avg_dur"], scale=chosen_evt["avg_dur"] * 0.3)),
                        )
                        event_offset = int(rng.integers(10, 300))
                        event_ts = session_timestamp + timedelta(seconds=event_offset)

                        e_id = f"EVT_{evt_counter:08d}"
                        evt_counter += 1
                        events.append({
                            "event_id": e_id,
                            "user_id": u_id,
                            "event_timestamp": event_ts.strftime("%Y-%m-%d %H:%M:%S"),
                            "event_date": event_ts.strftime("%Y-%m-%d"),
                            "event_type": chosen_evt["type"],
                            "feature_name": chosen_evt["feature"],
                            "session_duration_seconds": dur,
                            "notification_opened": chosen_evt["type"] == "notification_opened",
                            "session_number": user_session_num,
                        })

                    user_session_num += 1

            current_dt += timedelta(days=1)

        # Churn Label Definition:
        # A user is churned (1) if they had 0 active sessions during the 30-day outcome window
        # Retained (0) if they had >= 1 active session in the outcome window
        is_churned = 1 if sessions_in_outcome_window == 0 else 0

        churn_records.append({
            "user_id": u_id,
            "observation_cutoff_date": cutoff_date.strftime("%Y-%m-%d"),
            "outcome_window_days": 30,
            "outcome_sessions_count": sessions_in_outcome_window,
            "churn_label": is_churned,
        })

    activity_df = pd.DataFrame(events)
    churn_df = pd.DataFrame(churn_records)

    logger.info("Generated %d events and %d churn records.", len(activity_df), len(churn_df))
    return activity_df, churn_df


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic data for AstroGuide AI.")
    parser.add_argument("--users", type=int, default=10000, help="Number of synthetic users (default: 10000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--output-dir", type=str, default="data/raw", help="Output directory for CSV files")
    args = parser.parse_args()

    rng = np.random.default_rng(seed=args.seed)
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Timeline design:
    # Signups: 2025-01-01 to 2025-07-31 (7 months)
    # Observation Cutoff: 2025-08-31 (All users have at least 31 days tenure before cutoff)
    # Outcome Window: 2025-09-01 to 2025-09-30 (30 days for ground-truth churn measurement)
    signup_start = datetime(2025, 1, 1)
    signup_end = datetime(2025, 7, 31)
    cutoff_date = datetime(2025, 8, 31)
    outcome_end_date = datetime(2025, 9, 30)

    logger.info("Starting synthetic dataset generation pipeline...")
    logger.info("Timeline: Signups [%s to %s] | Cutoff: %s | Outcome: [%s to %s]",
                signup_start.strftime("%Y-%m-%d"), signup_end.strftime("%Y-%m-%d"),
                cutoff_date.strftime("%Y-%m-%d"),
                (cutoff_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                outcome_end_date.strftime("%Y-%m-%d"))

    # 1. Users
    users_df = generate_users(args.users, signup_start, signup_end, rng)
    users_file = output_path / "users.csv"
    users_df.to_csv(users_file, index=False)
    logger.info("Saved users to %s (%d rows)", users_file, len(users_df))

    # 2. Subscriptions
    subs_df, _ = generate_subscriptions(users_df, cutoff_date, rng)
    subs_file = output_path / "subscriptions.csv"
    subs_df.to_csv(subs_file, index=False)
    logger.info("Saved subscriptions to %s (%d rows)", subs_file, len(subs_df))

    # 3. Transactions
    txns_df = generate_transactions(subs_df, users_df, cutoff_date, rng)
    txns_file = output_path / "transactions.csv"
    txns_df.to_csv(txns_file, index=False)
    logger.info("Saved transactions to %s (%d rows)", txns_file, len(txns_df))

    # 4. Activity Telemetry & Churn Labels
    activity_df, churn_df = generate_activity_and_churn(
        users_df, subs_df, signup_start, cutoff_date, outcome_end_date, rng
    )
    activity_file = output_path / "user_activity.csv"
    activity_df.to_csv(activity_file, index=False)
    logger.info("Saved activity to %s (%d rows)", activity_file, len(activity_df))

    churn_file = output_path / "churn_labels.csv"
    churn_df.to_csv(churn_file, index=False)
    logger.info("Saved churn labels to %s (%d rows)", churn_file, len(churn_df))

    logger.info("Dataset generation completed successfully!")


if __name__ == "__main__":
    main()
