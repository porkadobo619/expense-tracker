# Expense Tracker — Personal Expense Service

A personal expense and budget tracking microservice built with Python, FastAPI, and SQLite,
fronted by an nginx gateway and a lightweight PWA. Built as an OOP-based microservice project.

## Quick start (Docker)

    docker compose up --build

Then open:
- App: http://localhost:8080/
- API docs: http://localhost:8080/docs
- Health check: http://localhost:8080/api/health

To stop: `Ctrl+C`, then `docker compose down`.

## Run without Docker (for development)

    cd expense-service
    python -m venv .venv
    .venv\Scripts\Activate.ps1        (Windows)
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://localhost:8000/docs

## Running tests

    cd expense-service
    .venv\Scripts\Activate.ps1
    python -m pytest

27 tests covering domain logic, the repository (in-memory and SQLite), the service layer,
and the API end to end.

## Architecture

    PWA (browser) -> Gateway (nginx) -> Expense Service (FastAPI) -> SQLite

The Expense Service owns all transaction and budget data — one business capability, one
data owner. The gateway is the single entry point for the frontend and proxies /api/* to
the service.

## Design notes

- `Transaction` is abstract; `Expense` and `Income` implement `signed_amount()` differently,
  so totals never need an if/else on type.
- `Money` stores centavos as an integer to avoid floating-point rounding errors.
- `TransactionRepository` is an interface. `ExpenseTrackerService` depends on it, not on
  SQLite directly, so swapping the in-memory implementation for SQLite required no changes
  to the service or API layer.
- Invalid input (negative amounts, empty categories, out-of-range months) is rejected with
  a 422 and a clear JSON error, not a stack trace.
- The gateway returns a clear 503 JSON error if the expense service is unreachable, instead
  of crashing or hanging.

## Known limitations

- Budget limits are stored in memory and reset when the service restarts. Transaction data
  persists in SQLite.
- The PWA is a single-page interface without offline support or installability yet.

## Reflection

The interface-based repository was the design decision that paid off the most: moving from
an in-memory store to SQLite was a single new file and a one-line change in `main.py`, with
zero changes to the service layer or API. The main trade-off was keeping budgets in memory
for now rather than adding another table — a reasonable scope cut for a solo project on a
deadline, and the next clear improvement.