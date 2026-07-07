import os
import sys
import tempfile
from types import SimpleNamespace

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Point the app at an isolated throwaway DB *before* importing anything from
# `app`, since Settings()/engine are constructed at import time.
_tmp_db = os.path.join(tempfile.mkdtemp(), "test_saarthi.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp_db}"

import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.db.seed import DEMO_CHAT_TURNS
from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_login_known_demo_customer(client):
    r = client.post("/auth/login", json={"customer_id": settings.demo_customer_id})
    assert r.status_code == 200
    body = r.json()
    assert body["customer_id"] == settings.demo_customer_id
    assert "token" in body


def test_login_unknown_customer_404(client):
    r = client.post("/auth/login", json={"customer_id": "NOPE"})
    assert r.status_code == 404


def test_profile(client):
    r = client.get(f"/users/{settings.demo_customer_id}/profile")
    assert r.status_code == 200
    body = r.json()
    assert body["customer_id"] == settings.demo_customer_id
    assert body["monthly_income"] > 0


def test_wealth_summary(client):
    r = client.get(f"/users/{settings.demo_customer_id}/wealth-summary")
    assert r.status_code == 200
    body = r.json()
    assert 0 <= body["wealth_health_score"] <= 100
    assert set(body["health_score_breakdown"]) == {"savings", "sip_discipline", "diversification", "credit_health"}


def test_risk_profile(client):
    r = client.get(f"/users/{settings.demo_customer_id}/risk-profile")
    assert r.status_code == 200
    body = r.json()
    assert body["risk_label"] in {"conservative", "moderate", "aggressive"}
    assert abs(sum(body["class_probabilities"].values()) - 1.0) < 1e-3


def test_goals_seeded(client):
    r = client.get(f"/users/{settings.demo_customer_id}/goals")
    assert r.status_code == 200
    goals = r.json()
    assert len(goals) == 3
    assert all("funded_pct" in g for g in goals)


def test_create_goal(client):
    payload = {"name": "Test Goal", "target_amount": 100000, "target_years": 5, "current_amount": 10000, "monthly_contribution": 1000}
    r = client.post(f"/users/{settings.demo_customer_id}/goals", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Test Goal"
    assert body["funded_pct"] == 10.0


def test_recommendations(client):
    r = client.get(f"/users/{settings.demo_customer_id}/recommendations")
    assert r.status_code == 200
    body = r.json()
    assert body["recommended_equity_pct"] + body["recommended_debt_pct"] == pytest.approx(100.0)
    assert len(body["goal_suggestions"]) >= 3


def test_nudges(client):
    r = client.get(f"/users/{settings.demo_customer_id}/nudges")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_chat_fallback(client):
    r = client.post("/chat", json={"customer_id": settings.demo_customer_id, "message": "What's my risk profile?"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "fallback"  # no OPENAI_API_KEY set in test env
    assert len(body["reply"]) > 0


def test_avatar_service_uses_openai_when_configured(monkeypatch):
    from app.services import avatar_service

    monkeypatch.setattr(avatar_service.settings, "openai_api_key", "test-key")
    monkeypatch.setattr(avatar_service.settings, "openai_model", "gpt-4o-mini")

    class DummyCompletions:
        def create(self, **kwargs):
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="openai reply"))])

    class DummyClient:
        def __init__(self, api_key):
            self.chat = SimpleNamespace(completions=DummyCompletions())

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=DummyClient))

    assert avatar_service._llm_reply("hello", {"name": "Asha"}) == "openai reply"


def test_chat_unknown_customer(client):
    r = client.post("/chat", json={"customer_id": "NOPE", "message": "hi"})
    assert r.status_code == 404


def test_staff_login(client):
    r = client.post("/staff/login", json={"staff_id": settings.demo_staff_id, "password": settings.demo_staff_password})
    assert r.status_code == 200
    body = r.json()
    assert body["staff_id"] == settings.demo_staff_id
    assert "token" in body


def test_staff_login_wrong_password(client):
    r = client.post("/staff/login", json={"staff_id": settings.demo_staff_id, "password": "wrong"})
    assert r.status_code == 401


def _staff_auth_header(client):
    r = client.post("/staff/login", json={"staff_id": settings.demo_staff_id, "password": settings.demo_staff_password})
    token = r.json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_staff_endpoints_require_auth(client):
    assert client.get("/staff/customers").status_code in (401, 403)
    assert client.get(f"/staff/customers/{settings.demo_customer_id}/summary").status_code in (401, 403)


def test_staff_customer_list(client):
    headers = _staff_auth_header(client)
    r = client.get("/staff/customers", headers=headers)
    assert r.status_code == 200
    body = r.json()
    assert len(body) > 0
    assert all({"engagement_level", "top_product_label", "top_product_score"} <= set(item) for item in body)


def test_staff_customer_summary(client):
    headers = _staff_auth_header(client)
    r = client.get(f"/staff/customers/{settings.demo_customer_id}/summary", headers=headers)
    assert r.status_code == 200
    body = r.json()
    products = {o["product"] for o in body["opportunities"]}
    assert products == {"fd", "loan", "sip", "insurance"}
    assert all(0 <= o["score"] <= 100 for o in body["opportunities"])
    assert body["engagement"]["total_interactions"] > 0  # seeded demo chat turns
    assert "private to the customer" in body["chat_access_note"]


def test_staff_summary_never_exposes_raw_chat_content(client):
    headers = _staff_auth_header(client)
    r = client.get(f"/staff/customers/{settings.demo_customer_id}/summary", headers=headers)
    body_text = r.text
    for _, content, _ in DEMO_CHAT_TURNS:
        assert content not in body_text


def test_staff_customer_summary_unknown_customer(client):
    headers = _staff_auth_header(client)
    r = client.get("/staff/customers/NOPE/summary", headers=headers)
    assert r.status_code == 404
