from datetime import date
from app.domain.money import Money
from app.domain.transaction import Expense, Income
from app.domain.sqlite_repository import SqliteTransactionRepository


def make_repo(tmp_path):
    return SqliteTransactionRepository(str(tmp_path / "test.db"))


def test_add_and_get(tmp_path):
    repo = make_repo(tmp_path)
    e = Expense(Money.of(150), "Food", date(2026, 9, 15), "lunch")
    tx_id = repo.add(e)
    fetched = repo.get(tx_id)
    assert fetched.amount == Money.of(150)
    assert fetched.category == "Food"
    assert fetched.note == "lunch"


def test_list_by_month_filters_correctly(tmp_path):
    repo = make_repo(tmp_path)
    repo.add(Expense(Money.of(100), "Food", date(2026, 9, 5)))
    repo.add(Expense(Money.of(200), "Food", date(2026, 8, 5)))
    repo.add(Income(Money.of(500), "Salary", date(2026, 9, 20)))
    september = repo.list_by_month(2026, 9)
    assert len(september) == 2


def test_delete_removes_transaction(tmp_path):
    repo = make_repo(tmp_path)
    tx_id = repo.add(Expense(Money.of(50), "Transport", date(2026, 9, 1)))
    assert repo.delete(tx_id) is True
    assert repo.get(tx_id) is None


def test_persists_across_reconnect(tmp_path):
    db_file = str(tmp_path / "persist.db")
    repo1 = SqliteTransactionRepository(db_file)
    tx_id = repo1.add(Expense(Money.of(75), "Food", date(2026, 9, 10)))

    repo2 = SqliteTransactionRepository(db_file)
    fetched = repo2.get(tx_id)
    assert fetched is not None
    assert fetched.amount == Money.of(75)
