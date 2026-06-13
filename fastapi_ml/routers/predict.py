"""Prediction and training endpoints."""
from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException

import model_service
from schemas import (
    FeatureScore, PredictionResult, StudentFeatures,
    TrainRequest, TrainResponse,
)

router = APIRouter(tags=["predict"])
logger = logging.getLogger("acadpredict.routers.predict")

HERE = Path(__file__).resolve().parent.parent
BIAS_REPORT_PATH = HERE / "ml" / "bias_report.json"


@router.post("/predict", response_model=PredictionResult)
async def predict_single(student: StudentFeatures) -> PredictionResult:
    try:
        return await asyncio.to_thread(model_service.predict, student)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/predict-bulk", response_model=list[PredictionResult])
async def predict_bulk(students: list[StudentFeatures]) -> list[PredictionResult]:
    if not students:
        raise HTTPException(status_code=422, detail="No student records supplied.")
    try:
        tasks = [asyncio.to_thread(model_service.predict, s) for s in students]
        return await asyncio.gather(*tasks)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/feature-importance", response_model=list[FeatureScore])
async def get_feature_importance() -> list[FeatureScore]:
    try:
        return await asyncio.to_thread(model_service.feature_importance)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/bias-report")
async def get_bias_report() -> dict:
    """Return the most recent fairness/bias audit report."""
    if BIAS_REPORT_PATH.exists():
        return json.loads(BIAS_REPORT_PATH.read_text())
    return {"overall_accuracy": None, "subgroup_checks": [], "flags": []}


@router.post("/train", response_model=TrainResponse)
async def train_model(request: TrainRequest) -> TrainResponse:
    """Retrain the model with real survey data blended with synthetic rows."""
    from ml.train_model import train_with_real_data

    try:
        real_rows = []
        for tr in request.rows:
            row = dict(tr.features)
            row["performance_class"] = tr.label
            real_rows.append(row)

        accuracy, total, bias_report = await asyncio.to_thread(
            train_with_real_data,
            real_rows,
            request.use_synthetic,
            request.synthetic_n,
        )
        model_service.reload_artifacts()
        logger.info("Model retrained with %d rows. Accuracy=%.3f", total, accuracy)
        return TrainResponse(
            success=True,
            message=f"Model retrained successfully with {total} total rows.",
            rows_used=total,
            accuracy=round(accuracy, 4),
            bias_report=bias_report,
        )
    except Exception as exc:
        logger.exception("Training failed: %s", exc)
        raise HTTPException(status_code=500, detail=f"Training failed: {exc}") from exc
