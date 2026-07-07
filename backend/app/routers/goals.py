from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer, Goal
from app.schemas import GoalCreate, GoalOut
from app.services.goal_service import goal_to_dict

router = APIRouter(prefix="/users/{customer_id}/goals", tags=["goals"])


@router.get("", response_model=list[GoalOut])
def list_goals(customer_id: str, db: Session = Depends(get_db)):
    goals = db.query(Goal).filter_by(customer_id=customer_id).all()
    return [goal_to_dict(g) for g in goals]


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(customer_id: str, payload: GoalCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    goal = Goal(
        customer_id=customer_id,
        name=payload.name,
        target_amount=payload.target_amount,
        current_amount=payload.current_amount,
        target_years=payload.target_years,
        years_elapsed=0,
        monthly_contribution=payload.monthly_contribution,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal_to_dict(goal)
