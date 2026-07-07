from app.db.models import Customer


def _clip(v, lo, hi):
    return max(lo, min(hi, v))


def compute_wealth_summary(customer: Customer) -> dict:
    savings_score = _clip((customer.savings_rate or 0) / 0.30, 0, 1) * 100

    if not customer.sip_active:
        sip_score = 35.0
        sip_status = "Not started"
    elif customer.sip_missed_last_6m == 0:
        sip_score = 100.0
        sip_status = "Healthy"
    else:
        sip_score = _clip(100 - customer.sip_missed_last_6m * 16, 0, 100)
        sip_status = "Needs attention"

    equity = customer.equity_pct_current or 0
    # a 40-70% equity band is treated as a "balanced" allocation for a mid-horizon goal mix
    if 40 <= equity <= 70:
        diversification_score = 100.0
    else:
        distance = min(abs(equity - 40), abs(equity - 70))
        diversification_score = _clip(100 - distance * 1.8, 0, 100)

    credit_score = _clip(100 - (customer.credit_card_utilization_pct or 0), 0, 100)

    weights = {"savings": 0.30, "sip": 0.25, "diversification": 0.20, "credit": 0.25}
    overall = (
        savings_score * weights["savings"]
        + sip_score * weights["sip"]
        + diversification_score * weights["diversification"]
        + credit_score * weights["credit"]
    )

    portfolio_value = (customer.existing_investment_value or 0)

    return {
        "portfolio_value": round(portfolio_value, 2),
        "monthly_savings": round(customer.monthly_savings or 0, 2),
        "savings_rate": round(customer.savings_rate or 0, 4),
        "wealth_health_score": round(overall),
        "health_score_breakdown": {
            "savings": round(savings_score),
            "sip_discipline": round(sip_score),
            "diversification": round(diversification_score),
            "credit_health": round(credit_score),
        },
        "sip_status": sip_status,
    }
