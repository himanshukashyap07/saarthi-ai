"""Turns a customer's behavioral profile into bank-staff-facing sales signals:
suitability scores for the products IDBI's frontline actually sells (FD, loan,
SIP, insurance) plus an engagement level derived from Saarthi chat activity.

This is explicitly the *staff-facing* counterpart to wealth_service.py's
customer-facing Wealth Health Score -- same rule-based/explainable philosophy,
different audience and purpose (conversion opportunity, not portfolio health).
Nothing here ever touches ChatMessage.content; only message counts/timestamps
feed the engagement score, so raw transcript text never leaves the customer's
own device/screen.
"""
import datetime as dt

from app.db.models import ChatMessage, Customer


def _clip(v, lo=0, hi=100):
    return max(lo, min(hi, v))


def _fd_suitability(c: Customer) -> tuple[int, str]:
    invested_ratio = _clip((c.sip_amount or 0) / max(c.monthly_savings or 1, 1), 0, 1)
    idle_component = (1 - invested_ratio) * 100
    conservative_component = _clip(c.debt_pct_current or 0)
    horizon_component = _clip(100 - (c.goal_horizon_years or 0) * 8)
    age_component = _clip(((c.age or 30) - 25) * 2)

    score = round(
        idle_component * 0.35
        + conservative_component * 0.30
        + horizon_component * 0.20
        + age_component * 0.15
    )
    rationale = (
        f"{round(idle_component)}% of savings sit uninvested and the current "
        f"{round(conservative_component)}% debt allocation both point to a "
        "capital-safe, fixed-return appetite."
    )
    return score, rationale


def _loan_eligibility(c: Customer) -> tuple[int, str]:
    expense_ratio = (c.monthly_expense or 0) / max(c.monthly_income or 1, 1)
    dti_component = _clip(100 - expense_ratio * 100)
    credit_component = _clip(100 - (c.credit_card_utilization_pct or 0))
    stability_component = _clip((c.savings_rate or 0) / 0.25 * 100)
    dependents_component = _clip(100 - (c.dependents or 0) * 15)

    score = round(
        dti_component * 0.35
        + credit_component * 0.30
        + stability_component * 0.20
        + dependents_component * 0.15
    )
    rationale = (
        f"Expense-to-income ratio of {round(expense_ratio * 100)}% and "
        f"{round(c.credit_card_utilization_pct or 0)}% card utilization "
        "indicate healthy repayment capacity."
    )
    return score, rationale


def _sip_fit(c: Customer) -> tuple[int, str]:
    capacity_component = _clip((c.monthly_savings or 0) / max(c.monthly_income or 1, 1) * 200)
    if not c.sip_active:
        headroom_component = 90.0
    else:
        headroom_component = _clip(100 - (c.sip_amount or 0) / max(c.monthly_savings or 1, 1) * 100)
    horizon_component = _clip((c.goal_horizon_years or 0) * 7)
    age_component = _clip(100 - ((c.age or 30) - 22) * 2)

    score = round(
        capacity_component * 0.30
        + headroom_component * 0.30
        + horizon_component * 0.25
        + age_component * 0.15
    )
    if c.sip_active:
        rationale = "Existing SIP has room to grow given current savings capacity."
    else:
        rationale = f"No active SIP yet, but savings rate of {round((c.savings_rate or 0) * 100)}% shows spare capacity."
    return score, rationale


def _insurance_suitability(c: Customer) -> tuple[int, str]:
    dependents_component = _clip((c.dependents or 0) * 30)
    annual_income = max((c.monthly_income or 0) * 12, 1)
    coverage_ratio = (c.existing_investment_value or 0) / annual_income
    gap_component = _clip(100 - coverage_ratio * 10)
    age_component = _clip(100 - abs((c.age or 30) - 40) * 2.5)
    income_component = _clip((c.monthly_income or 0) / 100_000 * 100)

    score = round(
        dependents_component * 0.35
        + gap_component * 0.30
        + age_component * 0.20
        + income_component * 0.15
    )
    rationale = (
        f"{c.dependents or 0} dependent(s) and existing cover worth "
        f"~{round(coverage_ratio, 1)}x annual income suggest a protection gap."
    )
    return score, rationale


PRODUCTS = {
    "fd": ("Fixed Deposit", _fd_suitability),
    "loan": ("Personal Loan", _loan_eligibility),
    "sip": ("SIP / Mutual Fund", _sip_fit),
    "insurance": ("Insurance", _insurance_suitability),
}


def compute_opportunity_scores(customer: Customer) -> list[dict]:
    scores = []
    for key, (label, fn) in PRODUCTS.items():
        score, rationale = fn(customer)
        scores.append({"product": key, "label": label, "score": round(_clip(score)), "rationale": rationale})
    scores.sort(key=lambda s: s["score"], reverse=True)
    return scores


def compute_engagement(chat_messages: list[ChatMessage]) -> dict:
    user_turns = [m for m in chat_messages if m.role == "user"]
    total = len(user_turns)

    last_active = max((m.created_at for m in chat_messages), default=None)
    days_since = None
    if last_active is not None:
        now = dt.datetime.now(dt.timezone.utc)
        if last_active.tzinfo is None:
            last_active = last_active.replace(tzinfo=dt.timezone.utc)
        days_since = (now - last_active).days

    if total == 0:
        level = "No activity yet"
    elif total >= 6 and (days_since is None or days_since <= 14):
        level = "High"
    elif total >= 2:
        level = "Medium"
    else:
        level = "Low"

    return {
        "level": level,
        "total_interactions": total,
        "last_active": last_active,
        "days_since_last_active": days_since,
    }


def compute_staff_summary(customer: Customer, chat_messages: list[ChatMessage]) -> dict:
    opportunities = compute_opportunity_scores(customer)
    engagement = compute_engagement(chat_messages)
    top = opportunities[0]

    return {
        "customer_id": customer.customer_id,
        "name": customer.name,
        "age": customer.age,
        "occupation": customer.occupation,
        "engagement": engagement,
        "opportunities": opportunities,
        "top_opportunity": (
            f"{top['label']} is the strongest lead at {top['score']}% suitability."
        ),
        "chat_access_note": (
            "Raw chat transcript is private to the customer -- staff see only "
            "these aggregated scores, never the conversation itself."
        ),
    }
