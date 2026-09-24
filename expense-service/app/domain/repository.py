import uuid
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
from .transaction import Transaction


class TransactionRepository(ABC):
    @abstractmethod
    def add(self, transaction: Transaction) -> str:
        ...

    @abstractmethod
    def get(self, transaction_id: str) -> Optional[Transaction]:
        ...

    @abstractmethod
    def list_by_month(self, year: int, month: int) -> list[Transaction]:
        ...

    @abstractmethod
    def delete(self, transaction_id: str) -> bool:
        ...


class InMemoryTransactionRepository(TransactionRepository):
    def __init__(self):
        self._items: dict[str, Transaction] = {}

    def add(self, transaction: Transaction) -> str:
        transaction_id = str(uuid.uuid4())
        self._items[transaction_id] = transaction
        return transaction_id

    def get(self, transaction_id: str) -> Optional[Transaction]:
        return self._items.get(transaction_id)

    def list_by_month(self, year: int, month: int) -> list[Transaction]:
        return [
            tx for tx in self._items.values()
            if tx.date.year == year and tx.date.month == month
        ]

    def delete(self, transaction_id: str) -> bool:
        if transaction_id in self._items:
            del self._items[transaction_id]
            return True
        return False
