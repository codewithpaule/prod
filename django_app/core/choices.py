"""Canonical survey option sets.

Must stay in sync with ``fastapi_ml/ml/categories.py`` so that user input always
matches the categories the model was trained on.
"""
from __future__ import annotations

CATEGORIES: dict[str, list[str]] = {
    "gender": ["Male", "Female"],
    "age_range": ["16-18", "19-21", "22-24", "25+"],
    "level": ["100", "200", "300", "400", "500"],
    "study_hours": ["<1 hour", "1-2 hours", "3-4 hours", "5+ hours"],
    "attendance": ["<50%", "50-70%", "71-90%", ">90%"],
    "courses_failed": ["0", "1-2", "3-4", "5+"],
    "sleep_hours": ["<4 hours", "4-6 hours", "7-8 hours", ">8 hours"],
    "financial_stress": ["None", "Low", "Moderate", "High"],
    "mother_education": ["None", "Primary", "Secondary", "Tertiary", "Postgraduate"],
    "father_education": ["None", "Primary", "Secondary", "Tertiary", "Postgraduate"],
    "family_income": ["Low", "Lower-Middle", "Middle", "Upper-Middle", "High"],
    "part_time_work": ["No", "Yes - occasionally", "Yes - regularly"],
    "motivation": ["Low", "Moderate", "High"],
    "stress_level": ["Low", "Moderate", "High", "Severe"],
    "self_rated_perf": ["Poor", "Average", "Good", "Excellent"],
}

# Survey fields in the order they appear on forms and in CSV uploads.
SURVEY_FIELDS = [
    "student_ref",
    *CATEGORIES.keys(),
]


def choices_for(field: str) -> list[tuple[str, str]]:
    return [(value, value) for value in CATEGORIES[field]]
