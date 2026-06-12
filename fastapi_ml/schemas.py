"""Pydantic request/response models for the AcadPredict ML service."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

# Categorical features used by the model, in a fixed order.
FEATURE_FIELDS = [
    "gender",
    "age_range",
    "level",
    "study_hours",
    "attendance",
    "courses_failed",
    "sleep_hours",
    "financial_stress",
    "mother_education",
    "father_education",
    "family_income",
    "part_time_work",
    "motivation",
    "stress_level",
    "self_rated_perf",
]


class StudentFeatures(BaseModel):
    """Survey features for a single student."""

    student_ref: Optional[str] = Field(default=None, max_length=20)
    gender: str
    age_range: str
    level: str
    study_hours: str
    attendance: str
    courses_failed: str
    sleep_hours: str
    financial_stress: str
    mother_education: str
    father_education: str
    family_income: str
    part_time_work: str
    motivation: str
    stress_level: str
    self_rated_perf: str

    def feature_dict(self) -> dict[str, str]:
        return {field: getattr(self, field) for field in FEATURE_FIELDS}


class FeatureScore(BaseModel):
    feature: str
    importance: float


class PredictionResult(BaseModel):
    student_ref: Optional[str] = None
    predicted_class: str
    confidence: float
    recommendation: str
    feature_scores: list[FeatureScore]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
