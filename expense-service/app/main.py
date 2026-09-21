from fastapi import FastAPI

app = FastAPI(title="Expense Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok"}
