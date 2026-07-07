"""
Rule-based, explainable recommendation engine. The risk *label* comes from the
ML model (app.ml.risk_model); everything downstream -- asset allocation and
goal top-up sizing -- is a transparent formula so every number Saarthi shows a
customer can be traced back to a reason (SEBI/RBI explainability expectation).
"""
from app.db.models import Customer, Goal
from app.services.goal_service import goal_to_dict

RISK_EQUITY_MULTIPLIER = {"conservative": 0.65, "moderate": 1.0, "aggressive": 1.2}
RISK_ASSUMED_ANNUAL_RETURN = {"conservative": 0.07, "moderate": 0.09, "aggressive": 0.11}


def recommend_allocation(customer: Customer, risk_label: str) -> dict:
    base_equity = 110 - customer.age  # classic glide-path heuristic
    multiplier = RISK_EQUITY_MULTIPLIER.get(risk_label, 1.0)
    equity_pct = max(10.0, min(90.0, base_equity * multiplier))
    debt_pct = 100 - equity_pct

    rationale = (
        f"Base glide-path allocation for age {customer.age} is {base_equity:.0f}% equity; "
        f"adjusted by your '{risk_label}' behavioural profile (x{multiplier}) to "
        f"{equity_pct:.0f}% equity / {debt_pct:.0f}% debt."
    )
    return {
        "risk_label": risk_label,
        "recommended_equity_pct": round(equity_pct, 1),
        "recommended_debt_pct": round(debt_pct, 1),
        "rationale": rationale,
    }


def suggest_goal_topup(goal: Goal, risk_label: str) -> dict:
    g = goal_to_dict(goal)
    remaining_years = max(goal.target_years - goal.years_elapsed, 0.25)
    annual_return = RISK_ASSUMED_ANNUAL_RETURN.get(risk_label, 0.09)
    monthly_rate = (1 + annual_return) ** (1 / 12) - 1
    n_months = remaining_years * 12

    fv_of_current_corpus = goal.current_amount * ((1 + annual_return) ** remaining_years)
    fv_gap = max(goal.target_amount - fv_of_current_corpus, 0)

    if fv_gap == 0 or n_months <= 0:
        required_pmt = 0.0
    else:
        annuity_factor = (((1 + monthly_rate) ** n_months) - 1) / monthly_rate
        required_pmt = fv_gap / annuity_factor if annuity_factor > 0 else fv_gap / n_months

    topup = max(required_pmt - (goal.monthly_contribution or 0), 0)

    return {
        "goal_id": goal.id,
        "goal_name": goal.name,
        "funded_pct": g["funded_pct"],
        "on_track": g["on_track"],
        "assumed_annual_return_pct": round(annual_return * 100, 1),
        "required_monthly_contribution": round(required_pmt, 2),
        "current_monthly_contribution": goal.monthly_contribution,
        "suggested_topup": round(topup, 2),
    }
