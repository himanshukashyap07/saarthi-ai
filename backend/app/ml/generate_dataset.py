"""
Synthetic customer dataset generator for Saarthi's behavioural risk-profiling model.

There is no real IDBI customer data available in a hackathon prototype, so this
script fabricates a statistically-plausible dataset: financial features are drawn
from realistic Indian-retail-banking distributions, and the risk_label target is
produced by a hand-authored scoring formula (plus noise) that mimics how a human
relationship manager would judge suitability. The ML model in train_risk_model.py
then learns to recover this label from the raw features -- this is what lets the
recommendation engine infer a risk profile straight from behaviour instead of a
one-time static questionnaire.

Run: python -m app.ml.generate_dataset
"""
import os
import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 4000

OUT_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_PATH = os.path.join(OUT_DIR, "synthetic_customers.csv")

FIRST_NAMES = [
    "Aarav", "Ananya", "Rohit", "Priya", "Vikram", "Sneha", "Arjun", "Kavya",
    "Rahul", "Isha", "Karan", "Meera", "Aditya", "Divya", "Nikhil", "Pooja",
    "Sanjay", "Ritu", "Manish", "Neha", "Suresh", "Anjali", "Deepak", "Shreya",
]
LAST_NAMES = [
    "Sharma", "Verma", "Iyer", "Gupta", "Reddy", "Nair", "Patel", "Singh",
    "Das", "Menon", "Rao", "Chatterjee", "Joshi", "Kulkarni", "Bhatt", "Desai",
]
OCCUPATIONS = ["salaried", "self_employed", "business_owner"]


def generate(n=N_CUSTOMERS, seed=SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.integers(22, 61, size=n)
    occupation = rng.choice(OCCUPATIONS, size=n, p=[0.62, 0.23, 0.15])

    # income skews with age (career progression) and occupation, log-normal spread
    base_income = rng.lognormal(mean=10.6, sigma=0.45, size=n)  # ~ INR 30k-1.2L/mo median band
    age_bonus = (age - 22) * 900
    occ_mult = np.where(occupation == "business_owner", 1.25,
                 np.where(occupation == "self_employed", 1.05, 1.0))
    monthly_income = np.clip((base_income + age_bonus) * occ_mult, 18000, 800000).round(-2)

    # expense ratio varies by dependents & lifestyle noise
    dependents = rng.integers(0, 5, size=n)
    expense_ratio = np.clip(0.45 + dependents * 0.045 + rng.normal(0, 0.09, size=n), 0.28, 0.92)
    monthly_expense = (monthly_income * expense_ratio).round(-2)
    monthly_savings = np.maximum(monthly_income - monthly_expense, 0)
    savings_rate = np.where(monthly_income > 0, monthly_savings / monthly_income, 0)

    existing_investment_value = np.clip(
        rng.lognormal(mean=np.log(np.maximum(monthly_income * rng.uniform(2, 30, size=n), 1)), sigma=0.6),
        0, 15_000_000,
    ).round(-2)

    equity_pct_current = np.clip(rng.normal(45, 20, size=n), 0, 100).round(1)
    debt_pct_current = np.clip(100 - equity_pct_current - rng.uniform(0, 15, size=n), 0, 100).round(1)

    sip_active = rng.choice([0, 1], size=n, p=[0.35, 0.65])
    sip_amount = np.where(sip_active == 1, np.clip(monthly_savings * rng.uniform(0.2, 0.6, size=n), 500, 100000), 0).round(-2)
    sip_missed_last_6m = np.where(
        sip_active == 1,
        rng.poisson(lam=np.clip(1.6 - savings_rate * 2.5, 0.05, 3), size=n),
        0,
    )
    sip_missed_last_6m = np.clip(sip_missed_last_6m, 0, 6)

    # transaction volatility: coefficient of variation of monthly spend over 6 months (simulated)
    txn_volatility = np.clip(rng.normal(0.22, 0.09, size=n) + (1 - savings_rate) * 0.15, 0.03, 0.9).round(3)

    credit_card_utilization_pct = np.clip(rng.normal(35, 22, size=n) + (1 - savings_rate) * 20, 0, 100).round(1)

    goal_horizon_years = np.clip(rng.normal(11, 6, size=n) - dependents * 0.6, 1, 30).round(1)

    # ---- behavioural risk score (ground truth generator, not exposed to the model) ----
    z = (
        1.7 * (savings_rate - savings_rate.mean()) / (savings_rate.std() + 1e-6)
        + 1.1 * (goal_horizon_years - goal_horizon_years.mean()) / (goal_horizon_years.std() + 1e-6)
        - 1.3 * (age - age.mean()) / (age.std() + 1e-6)
        - 0.9 * (dependents - dependents.mean()) / (dependents.std() + 1e-6)
        - 1.0 * (credit_card_utilization_pct - credit_card_utilization_pct.mean()) / (credit_card_utilization_pct.std() + 1e-6)
        - 0.8 * (sip_missed_last_6m - sip_missed_last_6m.mean()) / (sip_missed_last_6m.std() + 1e-6)
        + 0.5 * (existing_investment_value - existing_investment_value.mean()) / (existing_investment_value.std() + 1e-6)
        + rng.normal(0, 0.55, size=n)  # noise so it isn't a trivially-linear-separable label
    )
    q1, q2 = np.quantile(z, [0.35, 0.7])
    risk_label = np.where(z <= q1, "conservative", np.where(z <= q2, "moderate", "aggressive"))

    customer_id = [f"SAARTHI{100000+i}" for i in range(n)]
    name = [f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}" for _ in range(n)]

    df = pd.DataFrame({
        "customer_id": customer_id,
        "name": name,
        "age": age,
        "occupation": occupation,
        "dependents": dependents,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense,
        "monthly_savings": monthly_savings,
        "savings_rate": savings_rate.round(4),
        "existing_investment_value": existing_investment_value,
        "equity_pct_current": equity_pct_current,
        "debt_pct_current": debt_pct_current,
        "sip_active": sip_active,
        "sip_amount": sip_amount,
        "sip_missed_last_6m": sip_missed_last_6m,
        "txn_volatility": txn_volatility,
        "credit_card_utilization_pct": credit_card_utilization_pct,
        "goal_horizon_years": goal_horizon_years,
        "risk_label": risk_label,
    })
    return df


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    df = generate()
    df.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(df)} synthetic customers to {OUT_PATH}")
    print(df["risk_label"].value_counts(normalize=True).round(3))


if __name__ == "__main__":
    main()
