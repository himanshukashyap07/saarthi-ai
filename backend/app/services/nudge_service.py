from app.db.models import Customer, Goal
from app.services.goal_service import goal_to_dict


def generate_nudges(customer: Customer, goals: list[Goal]) -> list[dict]:
    nudges: list[dict] = []

    if customer.sip_active and customer.sip_missed_last_6m >= 2:
        nudges.append({
            "type": "sip_lapse",
            "severity": "high",
            "title": "Your SIP has lapsed",
            "message": (
                f"You've missed {customer.sip_missed_last_6m} of your last 6 SIP instalments "
                f"of ₹{customer.sip_amount:,.0f}. Restarting it now keeps your goals on schedule."
            ),
        })

    if not customer.sip_active and (customer.monthly_savings or 0) > 5000:
        nudges.append({
            "type": "idle_cash",
            "severity": "medium",
            "title": "Idle savings could be working harder",
            "message": (
                f"You're saving about ₹{customer.monthly_savings:,.0f}/month that isn't invested yet. "
                "Starting a SIP could put this to work toward a goal."
            ),
        })

    if (customer.txn_volatility or 0) > 0.4 or (customer.savings_rate or 0) < 0.10:
        nudges.append({
            "type": "spend_volatility",
            "severity": "medium",
            "title": "Spending looks less predictable this period",
            "message": (
                "Your monthly spending has been swinging more than usual, which is squeezing your "
                "savings rate. A short review of discretionary categories could free up investable surplus."
            ),
        })

    if (customer.credit_card_utilization_pct or 0) > 60:
        nudges.append({
            "type": "credit_utilization",
            "severity": "high",
            "title": "High credit card utilisation",
            "message": (
                f"Your card utilisation is at {customer.credit_card_utilization_pct:.0f}%. Paying this down "
                "first usually beats the returns you'd earn by investing the same amount right now."
            ),
        })

    for goal in goals:
        g = goal_to_dict(goal)
        if not g["on_track"]:
            nudges.append({
                "type": "goal_drift",
                "severity": "medium",
                "title": f"'{goal.name}' is falling behind schedule",
                "message": (
                    f"'{goal.name}' is {g['funded_pct']}% funded after {goal.years_elapsed:.0f} of "
                    f"{goal.target_years:.0f} years. A top-up to your monthly contribution now can close the gap."
                ),
            })

    return nudges
