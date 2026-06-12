"""Domain services: persisting predictions from ML results."""
from __future__ import annotations

from django.db import transaction

from .choices import CATEGORIES
from .models import Prediction, Student


@transaction.atomic
def save_prediction(feature_data: dict, result: dict) -> Student:
    """Create/update a Student and its Prediction from an ML result dict."""
    student_ref = feature_data["student_ref"]
    defaults = {field: feature_data[field] for field in CATEGORIES}
    student, _ = Student.objects.update_or_create(
        student_ref=student_ref, defaults=defaults
    )
    Prediction.objects.update_or_create(
        student=student,
        defaults={
            "predicted_class": result["predicted_class"],
            "confidence": result["confidence"],
            "recommendation": result["recommendation"],
            "feature_scores": result.get("feature_scores", []),
            "model_version": "v1.0",
        },
    )
    return student
