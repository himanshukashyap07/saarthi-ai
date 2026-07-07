from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import BankStaff, ChatMessage, Customer
from app.schemas import StaffCustomerListItem, StaffCustomerSummary, StaffLoginRequest, StaffLoginResponse
from app.security import issue_staff_token, staff_id_from_token, verify_password
from app.services.opportunity_service import compute_engagement, compute_opportunity_scores, compute_staff_summary

router = APIRouter(prefix="/staff", tags=["staff"])
_bearer = HTTPBearer()


def get_current_staff(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> BankStaff:
    
    staff_id = staff_id_from_token(credentials.credentials)
    staff = db.query(BankStaff).filter_by(staff_id=staff_id).first() if staff_id else None
    if not staff:
        raise HTTPException(status_code=401, detail="Invalid or expired staff session")
    return staff


@router.post("/login", response_model=StaffLoginResponse)
def staff_login(payload: StaffLoginRequest, db: Session = Depends(get_db)):
    staff = db.query(BankStaff).filter_by(staff_id=payload.staff_id).first()
    if not staff or not verify_password(payload.password, staff.password_hash):
        raise HTTPException(status_code=401, detail="Invalid staff_id or password")

    token = issue_staff_token(staff.staff_id)
    return StaffLoginResponse(token=token, staff_id=staff.staff_id, name=staff.name, branch=staff.branch)


@router.get("/customers", response_model=list[StaffCustomerListItem])
def list_customers(
    db: Session = Depends(get_db),
    _staff: BankStaff = Depends(get_current_staff),
):
    items = []
    for customer in db.query(Customer).all():
        messages = db.query(ChatMessage).filter_by(customer_id=customer.customer_id).all()
        engagement = compute_engagement(messages)
        top = compute_opportunity_scores(customer)[0]
        items.append(StaffCustomerListItem(
            customer_id=customer.customer_id,
            name=customer.name,
            age=customer.age,
            occupation=customer.occupation,
            engagement_level=engagement["level"],
            top_product_label=top["label"],
            top_product_score=top["score"],
        ))
    items.sort(key=lambda i: i.top_product_score, reverse=True)
    return items


@router.get("/customers/{customer_id}/summary", response_model=StaffCustomerSummary)
def get_customer_summary(
    customer_id: str,
    db: Session = Depends(get_db),
    _staff: BankStaff = Depends(get_current_staff),
):
    customer = db.query(Customer).filter_by(customer_id=customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    messages = db.query(ChatMessage).filter_by(customer_id=customer_id).all()
    return compute_staff_summary(customer, messages)
