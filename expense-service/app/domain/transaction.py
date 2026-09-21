from abc import ABC, abstractmethod
from datetime import date
from .money import Money


class Transaction(ABC):
    def __init__(self, amount: Money, category: str, when: date, note: str = ""):
        if amount.centavos <= 0:
            raise ValueError("Amount must be positive")
        self._amount = amount
        self._category = category
        self._date = when
        self._note = note

    @property
    def amount(self):
        return self._amount

    @property
    def category(self):
        return self._category

    @property
    def date(self):
        return self._date

    @abstractmethod
    def signed_amount(self) -> int:
        ...


class Expense(Transaction):
    def signed_amount(self) -> int:
        return -self._amount.centavos


class Income(Transaction):
    def signed_amount(self) -> int:
        return self._amount.centavos
