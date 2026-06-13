"""Pydantic request/response models for the AcadPredict ML service."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

FEATURE_FIELDS = [
    "gender", "age_range", "level", "current_cgpa", "courses_failed",
    "father_education", "mother_education", "family_income", "household_size",
    "parental_involvement", "study_hours", "attendance", "class_prep",
    "resource_use", "sleep_hours", "group_study", "past_questions",
    "part_time_work", "distance", "internet_access", "extracurricular",
    "family_responsibilities", "stress_level", "course_interest",
    "motivation", "self_rated_perf",
]


class StudentFeatures(BaseModel):
    student_ref: Optional[str] = Field(default=None, max_length=30)
    gender: str
    age_range: str
    level: str
    current_cgpa: str
    courses_failed: str
    father_education: str
    mother_education: str
    family_income: str
    household_size: str
    parental_involvement: str
    study_hours: str
    attendance: str
    class_prep: str
    resource_use: str
    sleep_hours: str
    group_study: str
    past_questions: str
    part_time_work: str
    distance: str
    internet_access: str
    extracurricular: str
    family_responsibilities: str
    stress_level: str
    course_interest: str
    motivation: str
    self_rated_perf: str

    def feature_dict(self) -> dict[str, str]:
        return {field: getattr(self, field) for field in FEATURE_FIELDS}


class TrainingRow(BaseModel):
    features: dict[str, str]
    label: str


class TrainRequest(BaseModel):
    rows: list[TrainingRow]
    use_synthetic: bool = True
    synthetic_n: int = Field(default=3000, ge=100, le=10000)


class TrainResponse(BaseModel):
    success: bool
    message: str
    rows_used: int
    accuracy: Optional[float] = None


class FeatureScore(BaseModel):
    feature: str
    importance: float


class PredictionResult(BaseModel):
    student_ref: Optional[str] = None
    predicted_class: str
    estimated_cgpa_range: str
    estimated_cgpa_midpoint: float
    confidence: float
    recommendation: str
    feature_scores: list[FeatureScore]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    version: str
