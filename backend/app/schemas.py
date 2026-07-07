import datetime as dt

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    customer_id: str = Field(..., examples=["SAARTHI100000"])


class LoginResponse(BaseModel):
    token: str
    customer_id: str
    name: str


class CustomerProfile(BaseModel):
    customer_id: str
    name: str
    age: int
    occupation: str
    dependents: int
    monthly_income: float
    monthly_expense: float
    monthly_savings: float
    savings_rate: float
    existing_investment_value: float
    equity_pct_current: float
    debt_pct_current: float
    sip_active: bool
    sip_amount: float
    sip_missed_last_6m: int
    goal_horizon_years: float

    model_config = {"from_attributes": True}


class WealthSummary(BaseModel):
    portfolio_value: float
    monthly_savings: float
    savings_rate: float
    wealth_health_score: int
    health_score_breakdown: dict[str, int]
    sip_status: str


class RiskProfileResponse(BaseModel):
    risk_label: str
    confidence: float
    class_probabilities: dict[str, float]
    model_ready: bool


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    target_years: float
    current_amount: float = 0
    monthly_contribution: float = 0


class GoalOut(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    target_years: float
    years_elapsed: float
    monthly_contribution: float
    funded_pct: float
    on_track: bool

    model_config = {"from_attributes": True}


class RecommendationResponse(BaseModel):
    risk_label: str
    recommended_equity_pct: float
    recommended_debt_pct: float
    rationale: str
    goal_suggestions: list[dict]


class NudgeOut(BaseModel):
    type: str
    severity: str
    title: str
    message: str


class ChatRequest(BaseModel):
    customer_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    source: str  # "llm" | "fallback"


class StaffLoginRequest(BaseModel):
    staff_id: str = Field(..., examples=["STAFF001"])
    password: str = Field(..., examples=["saarthi-demo"])


class StaffLoginResponse(BaseModel):
    token: str
    staff_id: str
    name: str
    branch: str | None = None


class OpportunityScore(BaseModel):
    product: str
    label: str
    score: int
    rationale: str


class EngagementSummary(BaseModel):
    level: str
    total_interactions: int
    last_active: dt.datetime | None = None
    days_since_last_active: int | None = None


class StaffCustomerListItem(BaseModel):
    customer_id: str
    name: str
    age: int
    occupation: str
    engagement_level: str
    top_product_label: str
    top_product_score: int


class StaffCustomerSummary(BaseModel):
    customer_id: str
    name: str
    age: int
    occupation: str
    engagement: EngagementSummary
    opportunities: list[OpportunityScore]
    top_opportunity: str
    chat_access_note: str
