from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, Goal, ChatMessage
from app.ml.risk_model import predict_risk_profile, is_ready
from app.schemas import ChatRequest, ChatResponse
from app.services.goal_service import goal_to_dict
from app.services.wealth_service import compute_wealth_summary
from app.services.avatar_service import get_avatar_reply

router = APIRouter(prefix="/chat", tags=["chat"])


def _build_context(customer: Customer, db: Session) -> dict:
    goals = db.query(Goal).filter_by(customer_id=customer.customer_id).all()
    wealth = compute_wealth_summary(customer)

    risk_label = "moderate"
    if is_ready():
        features = {
            "age": customer.age, "dependents": customer.dependents,
            "monthly_income": customer.monthly_income, "monthly_expense": customer.monthly_expense,
            "monthly_savings": customer.monthly_savings, "savings_rate": customer.savings_rate,
            "existing_investment_value": customer.existing_investment_value,
            "equity_pct_current": customer.equity_pct_current, "debt_pct_current": customer.debt_pct_current,
            "sip_active": int(customer.sip_active), "sip_amount": customer.sip_amount,
            "sip_missed_last_6m": customer.sip_missed_last_6m, "txn_volatility": customer.txn_volatility,
            "credit_card_utilization_pct": customer.credit_card_utilization_pct,
            "goal_horizon_years": customer.goal_horizon_years, "occupation": customer.occupation,
        }
        try:
            risk_label = predict_risk_profile(features)["risk_label"]
        except Exception:
            pass

    return {
        "name": customer.name,
        "risk_label": risk_label,
        "wealth_health_score": wealth["wealth_health_score"],
        "goals": [goal_to_dict(g) for g in goals],
    }


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter_by(customer_id=payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    context = _build_context(customer, db)
    result = get_avatar_reply(payload.message, context)

    db.add(ChatMessage(customer_id=customer.customer_id, role="user", content=payload.message, source="user"))
    db.add(ChatMessage(customer_id=customer.customer_id, role="avatar", content=result["reply"], source=result["source"]))
    db.commit()

    return ChatResponse(**result)
