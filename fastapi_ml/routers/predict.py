"""Prediction endpoints: single, bulk, and feature importance."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, HTTPException

import model_service
from schemas import FeatureScore, PredictionResult, StudentFeatures

router = APIRouter(tags=["predict"])


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
