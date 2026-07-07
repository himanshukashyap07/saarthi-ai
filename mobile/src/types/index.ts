export interface CustomerProfile {
  customer_id: string;
  name: string;
  age: number;
  occupation: string;
  dependents: number;
  monthly_income: number;
  monthly_expense: number;
  monthly_savings: number;
  savings_rate: number;
  existing_investment_value: number;
  equity_pct_current: number;
  debt_pct_current: number;
  sip_active: boolean;
  sip_amount: number;
  sip_missed_last_6m: number;
  goal_horizon_years: number;
}

export interface WealthSummary {
  portfolio_value: number;
  monthly_savings: number;
  savings_rate: number;
  wealth_health_score: number;
  health_score_breakdown: {
    savings: number;
    sip_discipline: number;
    diversification: number;
    credit_health: number;
  };
  sip_status: string;
}

export interface RiskProfile {
  risk_label: "conservative" | "moderate" | "aggressive";
  confidence: number;
  class_probabilities: Record<string, number>;
  model_ready: boolean;
}

export interface Goal {
  id: number;
  name: string;
  target_amount: number;
  current_amount: number;
  target_years: number;
  years_elapsed: number;
  monthly_contribution: number;
  funded_pct: number;
  on_track: boolean;
}

export interface GoalSuggestion {
  goal_id: number;
  goal_name: string;
  funded_pct: number;
  on_track: boolean;
  assumed_annual_return_pct: number;
  required_monthly_contribution: number;
  current_monthly_contribution: number;
  suggested_topup: number;
}

export interface Recommendation {
  risk_label: string;
  recommended_equity_pct: number;
  recommended_debt_pct: number;
  rationale: string;
  goal_suggestions: GoalSuggestion[];
}

export interface Nudge {
  type: string;
  severity: "low" | "medium" | "high";
  title: string;
  message: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "avatar";
  content: string;
  source?: "llm" | "fallback" | "user";
}

export interface LoginResponse {
  token: string;
  customer_id: string;
  name: string;
}

export interface StaffLoginResponse {
  token: string;
  staff_id: string;
  name: string;
  branch?: string;
}

export interface OpportunityScore {
  product: "fd" | "loan" | "sip" | "insurance";
  label: string;
  score: number;
  rationale: string;
}

export interface EngagementSummary {
  level: "High" | "Medium" | "Low" | "No activity yet";
  total_interactions: number;
  last_active: string | null;
  days_since_last_active: number | null;
}

export interface StaffCustomerListItem {
  customer_id: string;
  name: string;
  age: number;
  occupation: string;
  engagement_level: EngagementSummary["level"];
  top_product_label: string;
  top_product_score: number;
}

export interface StaffCustomerSummary {
  customer_id: string;
  name: string;
  age: number;
  occupation: string;
  engagement: EngagementSummary;
  opportunities: OpportunityScore[];
  top_opportunity: string;
  chat_access_note: string;
}
