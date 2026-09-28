import sqlite3
import uuid
from datetime import date
from typing import Optional
from .money import Money
from .transaction import Transaction, Expense, Income
from .repository import TransactionRepository


class SqliteTransactionRepository(TransactionRepository):
    def __init__(self, db_path: str = "expense_tracker.db"):
        self._db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self._db_path)

    def _init_db(self):
        conn = self._connect()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                centavos INTEGER NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()
        conn.close()

    def add(self, transaction: Transaction) -> str:
        transaction_id = str(uuid.uuid4())
        tx_type = "income" if isinstance(transaction, Income) else "expense"
        conn = self._connect()
        conn.execute(
            "INSERT INTO transactions (id, type, centavos, category, date, note) VALUES (?, ?, ?, ?, ?, ?)",
            (transaction_id, tx_type, transaction.amount.centavos, transaction.category,
             transaction.date.isoformat(), transaction.note),
        )
        conn.commit()
        conn.close()
        return transaction_id

    def get(self, transaction_id: str) -> Optional[Transaction]:
        conn = self._connect()
        row = conn.execute(
            "SELECT type, centavos, category, date, note FROM transactions WHERE id = ?",
            (transaction_id,),
        ).fetchone()
        conn.close()
        return self._row_to_transaction(row) if row else None

    def list_by_month(self, year: int, month: int) -> list[Transaction]:
        conn = self._connect()
        prefix = f"{year:04d}-{month:02d}"
        rows = conn.execute(
            "SELECT type, centavos, category, date, note FROM transactions WHERE date LIKE ?",
            (f"{prefix}%",),
        ).fetchall()
        conn.close()
        return [self._row_to_transaction(row) for row in rows]

    def delete(self, transaction_id: str) -> bool:
        conn = self._connect()
        cursor = conn.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        deleted = cursor.rowcount > 0
        conn.close()
        return deleted

    def _row_to_transaction(self, row) -> Transaction:
        tx_type, centavos, category, date_str, note = row
        amount = Money(centavos)
        when = date.fromisoformat(date_str)
        if tx_type == "income":
            return Income(amount, category, when, note)
        return Expense(amount, category, when, note)
