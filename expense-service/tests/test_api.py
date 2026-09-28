import pytest
from fastapi.testclient import TestClient
from app.main import create_app


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "api_test.db")))


def expense(amount=150, category="Food", when="2026-09-20"):
    return {"amount": amount, "category": category, "date": when, "note": "test"}


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_add_expense_and_summary(client):
    assert client.post("/expenses", json=expense()).status_code == 200
    summary = client.get("/summary/2026/9").json()
    assert summary["total_expense_centavos"] == 15000
    assert summary["by_category_centavos"]["Food"] == 15000


def test_add_income_updates_net(client):
    client.post("/income", json=expense(1000, "Salary"))
    client.post("/expenses", json=expense(300))
    summary = client.get("/summary/2026/9").json()
    assert summary["net_centavos"] == 70000


def test_delete_transaction_then_404(client):
    tx_id = client.post("/expenses", json=expense()).json()["id"]
    assert client.delete(f"/transactions/{tx_id}").status_code == 200
    assert client.delete(f"/transactions/{tx_id}").status_code == 404


def test_negative_amount_rejected(client):
    assert client.post("/expenses", json=expense(-50)).status_code == 422


def test_zero_amount_rejected(client):
    assert client.post("/expenses", json=expense(0)).status_code == 422


def test_empty_category_rejected(client):
    assert client.post("/expenses", json=expense(category="")).status_code == 422


def test_invalid_month_rejected(client):
    assert client.get("/summary/2026/13").status_code == 422


def test_budget_status_flow(client):
    client.put("/budgets", json={"category": "Food", "limit": 500})
    client.post("/expenses", json=expense(600))
    result = client.get("/budgets/Food/2026/9").json()
    assert result["status"] == "exceeded"


def test_error_response_has_no_stack_trace(client):
    resp = client.post("/expenses", json=expense(-5))
    assert resp.status_code == 422
    assert "Traceback" not in resp.text
