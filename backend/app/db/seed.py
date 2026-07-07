"""Seeds the SQLite DB from the synthetic dataset so the mobile app has real
data to render immediately, without a signup/data-aggregation flow."""
import datetime as dt
import os
import pandas as pd
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import BankStaff, ChatMessage, Customer, Goal
from app.security import hash_password

HERE = os.path.dirname(__file__)
CSV_PATH = os.path.join(HERE, "..", "ml", "data", "synthetic_customers.csv")

DEMO_GOALS = [
    # name, target_amount, target_years, years_elapsed, current_amount_ratio-of-target
    ("Retirement Corpus", 6_800_000, 28, 9, 0.62),
    ("Child's Education", 2_160_000, 12, 4, 0.38),
    ("Dream Home Down Payment", 2_900_000, 6, 2, 0.21),
]

# Seeded so the staff dashboard has real engagement/activity to show without
# requiring a demoer to chat first. Also doubles as a demo that "capture
# salary/EMI/goals through conversation" flow the onboarding feature describes.
DEMO_CHAT_TURNS = [
    ("user", "Hi Saarthi, can you look at my finances?", "user"),
    ("avatar", "Of course! I can see your income, savings and goals -- what would you like to check first?", "fallback"),
    ("user", "My salary is 80k and EMI is 15k, I want to buy a car in 2 years", "user"),
    ("avatar", "Got it -- I've noted that goal. A SIP of about ₹8,000/month could get you there.", "fallback"),
    ("user", "What about my FDs, is my cash just sitting idle?", "user"),
    ("avatar", "You do have some idle cash -- moving part of it to a high-yield FD could help.", "fallback"),
]


def seed(db: Session):
    if db.query(Customer).first() is not None:
        return  # already seeded

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(
            f"{CSV_PATH} not found — run: python -m app.ml.generate_dataset"
        )

    df = pd.read_csv(CSV_PATH).head(settings.seed_customer_count)

    for _, row in df.iterrows():
        db.add(Customer(
            customer_id=row["customer_id"],
            name=row["name"],
            age=int(row["age"]),
            occupation=row["occupation"],
            dependents=int(row["dependents"]),
            monthly_income=float(row["monthly_income"]),
            monthly_expense=float(row["monthly_expense"]),
            monthly_savings=float(row["monthly_savings"]),
            savings_rate=float(row["savings_rate"]),
            existing_investment_value=float(row["existing_investment_value"]),
            equity_pct_current=float(row["equity_pct_current"]),
            debt_pct_current=float(row["debt_pct_current"]),
            sip_active=bool(row["sip_active"]),
            sip_amount=float(row["sip_amount"]),
            sip_missed_last_6m=int(row["sip_missed_last_6m"]),
            txn_volatility=float(row["txn_volatility"]),
            credit_card_utilization_pct=float(row["credit_card_utilization_pct"]),
            goal_horizon_years=float(row["goal_horizon_years"]),
        ))
    db.commit()

    demo_id = settings.demo_customer_id
    demo_customer = db.query(Customer).filter_by(customer_id=demo_id).first()
    if demo_customer:
        for name, target, years, elapsed, funded_ratio in DEMO_GOALS:
            db.add(Goal(
                customer_id=demo_id,
                name=name,
                target_amount=target,
                current_amount=round(target * funded_ratio, 2),
                target_years=years,
                years_elapsed=elapsed,
                monthly_contribution=round((target - target * funded_ratio) / max((years - elapsed) * 12, 1), 2),
            ))

        now = dt.datetime.now(dt.timezone.utc)
        for i, (role, content, source) in enumerate(DEMO_CHAT_TURNS):
            db.add(ChatMessage(
                customer_id=demo_id,
                role=role,
                content=content,
                source=source,
                created_at=now - dt.timedelta(minutes=(len(DEMO_CHAT_TURNS) - i) * 3),
            ))
        db.commit()

    if db.query(BankStaff).first() is None:
        db.add(BankStaff(
            staff_id=settings.demo_staff_id,
            name="Priya Sharma",
            branch="IDBI Bandra Kurla Complex",
            password_hash=hash_password(settings.demo_staff_password),
        ))
        db.commit()

    print(f"Seeded {len(df)} customers. Demo customer_id = {demo_id}")
    print(f"Seeded demo bank staff login. staff_id = {settings.demo_staff_id}")
