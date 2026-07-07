import type {
  ChatMessage,
  CustomerProfile,
  Goal,
  LoginResponse,
  Nudge,
  Recommendation,
  RiskProfile,
  StaffCustomerListItem,
  StaffCustomerSummary,
  StaffLoginResponse,
  WealthSummary,
} from "@/types";


const API_BASE_URL = process.env.EXPO_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    throw new ApiError(res.status, body.detail ?? "Request failed");
  }
  return res.json() as Promise<T>;
}

export const api = {
  login: (customerId: string) =>
    request<LoginResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ customer_id: customerId }),
    }),

  getProfile: (customerId: string) =>
    request<CustomerProfile>(`/users/${customerId}/profile`),

  getWealthSummary: (customerId: string) =>
    request<WealthSummary>(`/users/${customerId}/wealth-summary`),

  getRiskProfile: (customerId: string) =>
    request<RiskProfile>(`/users/${customerId}/risk-profile`),

  getGoals: (customerId: string) => request<Goal[]>(`/users/${customerId}/goals`),

  createGoal: (
    customerId: string,
    goal: { name: string; target_amount: number; target_years: number; current_amount?: number; monthly_contribution?: number }
  ) =>
    request<Goal>(`/users/${customerId}/goals`, {
      method: "POST",
      body: JSON.stringify(goal),
    }),

  getRecommendations: (customerId: string) =>
    request<Recommendation>(`/users/${customerId}/recommendations`),

  getNudges: (customerId: string) => request<Nudge[]>(`/users/${customerId}/nudges`),

  sendChatMessage: (customerId: string, message: string) =>
    request<{ reply: string; source: ChatMessage["source"] }>("/chat", {
      method: "POST",
      body: JSON.stringify({ customer_id: customerId, message }),
    }),

  staffLogin: (staffId: string, password: string) =>
    request<StaffLoginResponse>("/staff/login", {
      method: "POST",
      body: JSON.stringify({ staff_id: staffId, password }),
    }),

  getStaffCustomers: (token: string) =>
    request<StaffCustomerListItem[]>("/staff/customers", {
      headers: { Authorization: `Bearer ${token}` },
    }),

  getStaffCustomerSummary: (token: string, customerId: string) =>
    request<StaffCustomerSummary>(`/staff/customers/${customerId}/summary`, {
      headers: { Authorization: `Bearer ${token}` },
    }),
};

export { ApiError, API_BASE_URL };
