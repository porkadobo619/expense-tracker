from datetime import date
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.domain.repository import InMemoryTransactionRepository
from app.domain.service import ExpenseTrackerService

app = FastAPI(title="Expense Service", version="1.0.0")

repository = InMemoryTransactionRepository()
service = ExpenseTrackerService(repository)


class TransactionIn(BaseModel):
    amount: float
    category: str
    date: date
    note: str = ""


class BudgetIn(BaseModel):
    category: str
    limit: float


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/expenses")
def add_expense(payload: TransactionIn):
    tx_id = service.add_expense(payload.amount, payload.category, payload.date, payload.note)
    return {"id": tx_id}


@app.post("/income")
def add_income(payload: TransactionIn):
    tx_id = service.add_income(payload.amount, payload.category, payload.date, payload.note)
    return {"id": tx_id}


@app.delete("/transactions/{transaction_id}")
def delete_transaction(transaction_id: str):
    deleted = service.delete_transaction(transaction_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"deleted": True}


@app.get("/summary/{year}/{month}")
def monthly_summary(year: int, month: int):
    return service.monthly_summary(year, month)


@app.put("/budgets")
def set_budget(payload: BudgetIn):
    service.set_budget(payload.category, payload.limit)
    return {"category": payload.category, "limit": payload.limit}


@app.get("/budgets/{category}/{year}/{month}")
def budget_status(category: str, year: int, month: int):
    return service.budget_status(category, year, month)
