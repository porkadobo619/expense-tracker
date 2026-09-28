import logging
import os
from datetime import date

from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.domain.sqlite_repository import SqliteTransactionRepository
from app.domain.service import ExpenseTrackerService

logger = logging.getLogger("expense_service")


class TransactionIn(BaseModel):
    amount: float = Field(gt=0, description="Amount in pesos, must be positive")
    category: str = Field(min_length=1)
    date: date
    note: str = ""


class BudgetIn(BaseModel):
    category: str = Field(min_length=1)
    limit: float = Field(gt=0)


def create_app(db_path: str = "expense_tracker.db") -> FastAPI:
    app = FastAPI(title="Expense Service", version="1.0.0")
    service = ExpenseTrackerService(SqliteTransactionRepository(db_path))

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=422,
            content={"error": "invalid_request", "detail": str(exc)},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error")
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "detail": "Something went wrong."},
        )

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
        if not service.delete_transaction(transaction_id):
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"deleted": True}

    @app.get("/summary/{year}/{month}")
    def monthly_summary(
        year: int = Path(ge=1900, le=2200),
        month: int = Path(ge=1, le=12),
    ):
        return service.monthly_summary(year, month)

    @app.put("/budgets")
    def set_budget(payload: BudgetIn):
        service.set_budget(payload.category, payload.limit)
        return {"category": payload.category, "limit": payload.limit}

    @app.get("/budgets/{category}/{year}/{month}")
    def budget_status(
        category: str,
        year: int = Path(ge=1900, le=2200),
        month: int = Path(ge=1, le=12),
    ):
        return service.budget_status(category, year, month)

    return app


app = create_app(os.getenv("EXPENSE_DB_PATH", "expense_tracker.db"))
