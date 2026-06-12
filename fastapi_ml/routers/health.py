"""Health-check endpoint."""
from __future__ import annotations

from fastapi import APIRouter

import model_service
from schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        model_loaded=model_service.is_loaded(),
        version=model_service.MODEL_VERSION,
    )
