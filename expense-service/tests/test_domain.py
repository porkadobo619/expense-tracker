from datetime import date
import pytest
from app.domain.money import Money
from app.domain.budget import Budget
from app.domain.transaction import Expense, Income


def test_money_arithmetic():
    assert Money.of(10.50).centavos == 1050
    assert Money.of(5).add(Money.of(2.5)) == Money.of(7.5)
    assert Money.of(5).subtract(Money.of(2)) == Money.of(3)


def test_budget_status():
    b = Budget("Food", Money.of(1000))
    assert b.status(Money.of(500)) == "ok"
    assert b.status(Money.of(800)) == "near"
    assert b.status(Money.of(1001)) == "exceeded"
    assert b.remaining(Money.of(300)) == Money.of(700)


def test_signed_amount_polymorphism():
    e = Expense(Money.of(100), "Food", date.today())
    i = Income(Money.of(100), "Salary", date.today())
    assert e.signed_amount() == -10000
    assert i.signed_amount() == 10000


def test_amount_must_be_positive():
    with pytest.raises(ValueError):
        Expense(Money.of(0), "Food", date.today())
