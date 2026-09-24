from datetime import date
from app.domain.money import Money
from app.domain.transaction import Expense, Income
from app.domain.repository import InMemoryTransactionRepository


def test_add_and_get():
    repo = InMemoryTransactionRepository()
    e = Expense(Money.of(150), "Food", date(2026, 9, 15))
    tx_id = repo.add(e)
    assert repo.get(tx_id) is e


def test_list_by_month_filters_correctly():
    repo = InMemoryTransactionRepository()
    repo.add(Expense(Money.of(100), "Food", date(2026, 9, 5)))
    repo.add(Expense(Money.of(200), "Food", date(2026, 8, 5)))
    repo.add(Income(Money.of(500), "Salary", date(2026, 9, 20)))

    september = repo.list_by_month(2026, 9)
    assert len(september) == 2


def test_delete_removes_transaction():
    repo = InMemoryTransactionRepository()
    tx_id = repo.add(Expense(Money.of(50), "Transport", date(2026, 9, 1)))
    assert repo.delete(tx_id) is True
    assert repo.get(tx_id) is None


def test_delete_nonexistent_returns_false():
    repo = InMemoryTransactionRepository()
    assert repo.delete("fake-id") is False
