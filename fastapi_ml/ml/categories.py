"""Canonical categorical option sets shared by training and serving.

These value sets are the single source of truth for the survey fields. The
Django forms expose the same options so that user input always matches what the
model was trained on.
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

PERFORMANCE_CLASSES = ["At-Risk", "Average", "High"]
