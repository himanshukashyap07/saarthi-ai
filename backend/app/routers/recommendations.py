from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, Goal
from app.ml.risk_model import predict_risk_profile, is_ready, ModelNotTrainedError
from app.schemas import RecommendationResponse
from app.services.recommendation_service import recommend_allocation, suggest_goal_topup

router = APIRouter(prefix="/users/{customer_id}/recommendations", tags=["recommendations"])


@router.get("", response_model=RecommendationResponse)
def get_recommendations(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    if not is_ready():
        raise HTTPException(status_code=503, detail="Risk model not trained yet.")

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
        risk_result = predict_risk_profile(features)
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))

    allocation = recommend_allocation(customer, risk_result["risk_label"])
    goals = db.query(Goal).filter_by(customer_id=customer_id).all()
    goal_suggestions = [suggest_goal_topup(g, risk_result["risk_label"]) for g in goals]

    return RecommendationResponse(
        risk_label=risk_result["risk_label"],
        recommended_equity_pct=allocation["recommended_equity_pct"],
        recommended_debt_pct=allocation["recommended_debt_pct"],
        rationale=allocation["rationale"],
        goal_suggestions=goal_suggestions,
    )
