from datetime import date
from .money import Money
from .transaction import Expense, Income, Transaction
from .budget import Budget
from .repository import TransactionRepository


class ExpenseTrackerService:
    def __init__(self, repository: TransactionRepository):
        self._repository = repository
        self._budgets: dict[str, Budget] = {}

    def add_expense(self, amount_pesos: float, category: str, when: date, note: str = "") -> str:
        expense = Expense(Money.of(amount_pesos), category, when, note)
        return self._repository.add(expense)

    def add_income(self, amount_pesos: float, category: str, when: date, note: str = "") -> str:
        income = Income(Money.of(amount_pesos), category, when, note)
        return self._repository.add(income)

    def delete_transaction(self, transaction_id: str) -> bool:
        return self._repository.delete(transaction_id)

    def set_budget(self, category: str, limit_pesos: float) -> None:
        self._budgets[category] = Budget(category, Money.of(limit_pesos))

    def monthly_summary(self, year: int, month: int) -> dict:
        transactions = self._repository.list_by_month(year, month)
        total_income = Money(0)
        total_expense = Money(0)
        by_category: dict[str, Money] = {}

        for tx in transactions:
            if isinstance(tx, Income):
                total_income = total_income.add(tx.amount)
            elif isinstance(tx, Expense):
                total_expense = total_expense.add(tx.amount)
                by_category[tx.category] = by_category.get(
                    tx.category, Money(0)
                ).add(tx.amount)

        return {
            "year": year,
            "month": month,
            "total_income_centavos": total_income.centavos,
            "total_expense_centavos": total_expense.centavos,
            "net_centavos": total_income.subtract(total_expense).centavos,
            "by_category_centavos": {k: v.centavos for k, v in by_category.items()},
        }

    def budget_status(self, category: str, year: int, month: int) -> dict:
        budget = self._budgets.get(category)
        if budget is None:
            return {"category": category, "has_budget": False}

        transactions = self._repository.list_by_month(year, month)
        spent = Money(0)
        for tx in transactions:
            if isinstance(tx, Expense) and tx.category == category:
                spent = spent.add(tx.amount)

        return {
            "category": category,
            "has_budget": True,
            "spent_centavos": spent.centavos,
            "limit_centavos": budget._limit.centavos,
            "status": budget.status(spent),
        }
