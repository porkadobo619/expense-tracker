from datetime import date
from app.domain.repository import InMemoryTransactionRepository
from app.domain.service import ExpenseTrackerService


def make_service():
    return ExpenseTrackerService(InMemoryTransactionRepository())


def test_add_expense_and_income():
    svc = make_service()
    svc.add_expense(200, "Food", date(2026, 9, 10))
    svc.add_income(1000, "Salary", date(2026, 9, 1))
    summary = svc.monthly_summary(2026, 9)
    assert summary["total_expense_centavos"] == 20000
    assert summary["total_income_centavos"] == 100000
    assert summary["net_centavos"] == 80000


def test_summary_groups_by_category():
    svc = make_service()
    svc.add_expense(100, "Food", date(2026, 9, 5))
    svc.add_expense(50, "Food", date(2026, 9, 6))
    svc.add_expense(300, "Bills", date(2026, 9, 7))
    summary = svc.monthly_summary(2026, 9)
    assert summary["by_category_centavos"]["Food"] == 15000
    assert summary["by_category_centavos"]["Bills"] == 30000


def test_budget_status_without_budget():
    svc = make_service()
    result = svc.budget_status("Food", 2026, 9)
    assert result["has_budget"] is False


def test_budget_status_exceeded():
    svc = make_service()
    svc.set_budget("Food", 500)
    svc.add_expense(600, "Food", date(2026, 9, 5))
    result = svc.budget_status("Food", 2026, 9)
    assert result["status"] == "exceeded"


def test_delete_transaction():
    svc = make_service()
    tx_id = svc.add_expense(100, "Food", date(2026, 9, 5))
    assert svc.delete_transaction(tx_id) is True
    summary = svc.monthly_summary(2026, 9)
    assert summary["total_expense_centavos"] == 0
