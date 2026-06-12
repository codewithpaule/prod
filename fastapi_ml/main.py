"""FastAPI application entry point for the AcadPredict ML/AI layer."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

import model_service
from routers import health, predict

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("acadpredict.ml")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup check: fail fast with a clear error if artifacts are missing.
    try:
        model_service.load_artifacts()
        logger.info("Model and preprocessor loaded successfully.")
    except FileNotFoundError as exc:
        logger.error("Startup model check failed: %s", exc)
    yield


app = FastAPI(
    title="AcadPredict ML API",
    version=model_service.MODEL_VERSION,
    description="Machine learning + Groq AI service for student performance prediction.",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(predict.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Ensure all errors return JSON with a 'detail' key (never HTML)."""
    logger.exception("Unhandled error on %s: %s", request.url.path, exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error."})


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    return {"service": "AcadPredict ML API", "docs": "/docs", "health": "/health"}
