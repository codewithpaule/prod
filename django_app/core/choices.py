"""Canonical survey option sets — mirrors fastapi_ml/ml/categories.py exactly.

Must stay in sync with ``fastapi_ml/ml/categories.py`` so that user input
always matches the categories the model was trained on.
"""
from __future__ import annotations

CATEGORIES: dict[str, list[str]] = {
    "gender": ["Male", "Female", "Prefer not to say"],
    "age_range": ["16-19", "20-23", "24-27", "28+"],
    "level": ["100", "200", "300", "400", "500"],
    "current_cgpa": [
        "First Class (4.5-5.0)",
        "Second Class Upper (3.5-4.4)",
        "Second Class Lower (2.5-3.4)",
        "Third Class (1.5-2.4)",
        "Below 1.5",
    ],
    "courses_failed": ["None", "1-2", "3-5", "More than 5"],
    "father_education": [
        "No formal education", "Primary", "Secondary",
        "OND/NCE", "Bachelor's degree", "Postgraduate",
    ],
    "mother_education": [
        "No formal education", "Primary", "Secondary",
        "OND/NCE", "Bachelor's degree", "Postgraduate",
    ],
    "family_income": [
        "Below \u20a650,000",
        "\u20a650,000-\u20a6150,000",
        "\u20a6150,000-\u20a6300,000",
        "\u20a6300,000-\u20a6500,000",
        "Above \u20a6500,000",
    ],
    "household_size": ["1-3", "4-6", "7-10", "More than 10"],
    "parental_involvement": ["Very involved", "Somewhat involved", "Not involved"],
    "study_hours": ["Less than 1 hour", "1-2 hours", "3-4 hours", "More than 4 hours"],
    "attendance": [
        "Always (90-100%)", "Often (70-89%)", "Sometimes (50-69%)", "Rarely (<50%)",
    ],
    "class_prep": ["Always", "Sometimes", "Rarely", "Never"],
    "resource_use": ["Very often", "Sometimes", "Rarely", "Never"],
    "sleep_hours": ["Less than 4 hours", "4-6 hours", "6-8 hours", "More than 8 hours"],
    "group_study": ["Yes regularly", "Occasionally", "No"],
    "past_questions": ["Always before exams", "Sometimes", "Rarely", "Never"],
    "part_time_work": ["Yes regularly", "Occasionally", "No"],
    "distance": [
        "On campus", "Less than 30 mins", "30 mins-1 hour", "More than 1 hour",
    ],
    "internet_access": [
        "Very stable", "Mostly stable", "Unstable", "Rarely have access",
    ],
    "extracurricular": ["Yes heavily involved", "Occasionally", "No"],
    "family_responsibilities": ["Not at all", "Slightly", "Moderately", "Significantly"],
    "stress_level": ["Low", "Moderate", "High", "Very high"],
    "course_interest": [
        "Yes my passion", "Partially interested",
        "No - family pressure", "No - no other choice",
    ],
    "motivation": ["Very high", "High", "Moderate", "Low"],
    "self_rated_perf": ["Excellent", "Good", "Average", "Poor", "Very Poor"],
}

SURVEY_FIELDS = ["student_ref", *CATEGORIES.keys()]


def choices_for(field: str) -> list[tuple[str, str]]:
    return [(value, value) for value in CATEGORIES[field]]
