"""Domain services: persisting predictions from ML results."""
from __future__ import annotations

from django.db import transaction

from .choices import CATEGORIES
from .models import Prediction, Student


@transaction.atomic
def save_prediction(feature_data: dict, result: dict) -> Student:
    """Create/update a Student and its Prediction from an ML result dict."""
    student_ref = feature_data['student_ref']
    defaults = {field: feature_data.get(field, '') for field in CATEGORIES}
    student, _ = Student.objects.update_or_create(
        student_ref=student_ref, defaults=defaults
    )
    Prediction.objects.update_or_create(
        student=student,
        defaults={
            'predicted_class': result['predicted_class'],
            'estimated_cgpa_range': result.get('estimated_cgpa_range', result['predicted_class']),
            'estimated_cgpa_midpoint': result.get('estimated_cgpa_midpoint', 2.95),
            'confidence': result['confidence'],
            'recommendation': result['recommendation'],
            'feature_scores': result.get('feature_scores', []),
            'model_version': 'v2.0',
        },
    )
    return student
