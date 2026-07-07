import base64

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Customer
from app.schemas import LoginRequest, LoginResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):

    customer = db.query(Customer).filter_by(customer_id=payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Unknown customer_id. Try the seeded demo_customer_id.")

    token = base64.b64encode(f"saarthi:{customer.customer_id}".encode()).decode()
    return LoginResponse(token=token, customer_id=customer.customer_id, name=customer.name)
