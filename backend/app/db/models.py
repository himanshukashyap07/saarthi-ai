import datetime as dt
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base


class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    occupation = Column(String)
    dependents = Column(Integer)

    monthly_income = Column(Float)
    monthly_expense = Column(Float)
    monthly_savings = Column(Float)
    savings_rate = Column(Float)

    existing_investment_value = Column(Float)
    equity_pct_current = Column(Float)
    debt_pct_current = Column(Float)

    sip_active = Column(Boolean, default=False)
    sip_amount = Column(Float, default=0)
    sip_missed_last_6m = Column(Integer, default=0)

    txn_volatility = Column(Float)
    credit_card_utilization_pct = Column(Float)
    goal_horizon_years = Column(Float)

    goals = relationship("Goal", back_populates="customer", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="customer", cascade="all, delete-orphan")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
    name = Column(String, nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)
    target_years = Column(Float, nullable=False)
    years_elapsed = Column(Float, default=0)
    monthly_contribution = Column(Float, default=0)
    created_at = Column(DateTime, default=lambda: dt.datetime.now(dt.timezone.utc))

    customer = relationship("Customer", back_populates="goals")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False)
    role = Column(String, nullable=False)  # "user" | "avatar"
    content = Column(String, nullable=False)
    source = Column(String, default="fallback")  # "llm" | "fallback"
    created_at = Column(DateTime, default=lambda: dt.datetime.now(dt.timezone.utc))

    customer = relationship("Customer", back_populates="chat_messages")


class BankStaff(Base):
    """A branch/RM login, distinct from the Customer table. Staff only ever see
    aggregated opportunity scores (app/services/opportunity_service.py) through
    the /staff router -- never a Customer's ChatMessage rows."""
    __tablename__ = "bank_staff"

    staff_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    branch = Column(String)
    password_hash = Column(String, nullable=False)
