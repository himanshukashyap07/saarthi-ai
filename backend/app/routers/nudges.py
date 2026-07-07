from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, Goal
from app.schemas import NudgeOut
from app.services.nudge_service import generate_nudges

router = APIRouter(prefix="/users/{customer_id}/nudges", tags=["nudges"])


@router.get("", response_model=list[NudgeOut])
def get_nudges(customer_id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    goals = db.query(Goal).filter_by(customer_id=customer_id).all()
    return generate_nudges(customer, goals)
