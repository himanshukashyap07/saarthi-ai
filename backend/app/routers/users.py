from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer
from app.ml.risk_model import predict_risk_profile, is_ready, ModelNotTrainedError
from app.schemas import CustomerProfile, WealthSummary, RiskProfileResponse
from app.services.wealth_service import compute_wealth_summary

router = APIRouter(prefix="/users", tags=["users"])


def _get_customer_or_404(customer_id: str, db: Session) -> Customer:
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.get("/{customer_id}/profile", response_model=CustomerProfile)
def get_profile(customer_id: str, db: Session = Depends(get_db)):
    return _get_customer_or_404(customer_id, db)


@router.get("/{customer_id}/wealth-summary", response_model=WealthSummary)
def get_wealth_summary(customer_id: str, db: Session = Depends(get_db)):
    customer = _get_customer_or_404(customer_id, db)
    return compute_wealth_summary(customer)


@router.get("/{customer_id}/risk-profile", response_model=RiskProfileResponse)
def get_risk_profile(customer_id: str, db: Session = Depends(get_db)):
    customer = _get_customer_or_404(customer_id, db)

    if not is_ready():
        raise HTTPException(
            status_code=503,
            detail="Risk model not trained yet. Run: python -m app.ml.generate_dataset && python -m app.ml.train_risk_model",
        )

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
        result = predict_risk_profile(features)
    except ModelNotTrainedError as e:
        raise HTTPException(status_code=503, detail=str(e))

    return RiskProfileResponse(**result, model_ready=True)
