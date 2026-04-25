"""FastAPI entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app import flags, storage

app = FastAPI(title="flag-eval")


class EvaluateRequest(BaseModel):
    flag: str
    user: str


class EvaluateResponse(BaseModel):
    enabled: bool
    variant: str | None = None
    reason: str


@app.get("/health")
def health() -> dict[str, str]:
    # NOTE: the warmup test expects `{"status": "ok"}`. Change this string to
    # make it pass — it's the only change needed for the warmup.
    return {"status": "healthy"}


@app.get("/flags")
def list_flags() -> list[dict]:
    return storage.all_flags()


@app.post("/evaluate", response_model=EvaluateResponse)
def evaluate(req: EvaluateRequest) -> EvaluateResponse:
    if not req.flag or not req.user:
        raise HTTPException(status_code=400, detail="flag and user are required")
    result = flags.evaluate(req.flag, req.user)
    return EvaluateResponse(**result)
