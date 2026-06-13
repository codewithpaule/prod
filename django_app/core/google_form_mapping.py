"""Maps Google Form export column headers and option values to model features.

When a user exports their Google Form responses as Excel/CSV, the column
headers are the full question text and option values may differ slightly from
our internal category values. This module normalises both.
"""
from __future__ import annotations

from .choices import CATEGORIES

COLUMN_MAP: dict[str, str] = {
    "what is your gender": "gender",
    "gender": "gender",
    "what is your age range": "age_range",
    "age range": "age_range",
    "what level are you currently in": "level",
    "what is your current level of study": "level",
    "current level of study": "level",
    "level of study": "level",
    "level": "level",
    "what is your current cgpa range": "current_cgpa",
    "current cgpa range": "current_cgpa",
    "cgpa range": "current_cgpa",
    "how many courses have you failed or are carrying over": "courses_failed",
    "courses failed": "courses_failed",
    "courses failed / carried over": "courses_failed",
    "what is your father's highest level of education": "father_education",
    "father's highest level of education": "father_education",
    "father education": "father_education",
    "father's education": "father_education",
    "what is your mother's highest level of education": "mother_education",
    "mother's highest level of education": "mother_education",
    "mother education": "mother_education",
    "mother's education": "mother_education",
    "what is your family's approximate monthly income level": "family_income",
    "family's approximate monthly income level": "family_income",
    "family income": "family_income",
    "monthly income": "family_income",
    "how many people are financially dependent in your household": "household_size",
    "financially dependent in your household": "household_size",
    "household size": "household_size",
    "how involved are your parents/guardians in your academic progress": "parental_involvement",
    "parental involvement": "parental_involvement",
    "parents/guardians involvement": "parental_involvement",
    "on average, how many hours do you spend studying per day": "study_hours",
    "how many hours do you spend studying per day": "study_hours",
    "on average, how many hours do you study per day outside class": "study_hours",
    "study hours per day": "study_hours",
    "study hours": "study_hours",
    "how often do you attend lectures": "attendance",
    "lecture attendance": "attendance",
    "attendance": "attendance",
    "how often do you read ahead before class": "class_prep",
    "how often do you read ahead or prepare before class": "class_prep",
    "read ahead or prepare before class": "class_prep",
    "class preparation": "class_prep",
    "class prep": "class_prep",
    "how often do you use academic resources": "resource_use",
    "use of academic resources": "resource_use",
    "resource use": "resource_use",
    "academic resources": "resource_use",
    "how many hours do you sleep on average per night": "sleep_hours",
    "sleep hours per night": "sleep_hours",
    "sleep hours": "sleep_hours",
    "do you participate actively in group study or discussions": "group_study",
    "do you participate in group study or academic discussions": "group_study",
    "group study or academic discussions": "group_study",
    "group study": "group_study",
    "how often do you practice past exam questions": "past_questions",
    "practice past exam questions": "past_questions",
    "past questions": "past_questions",
    "do you engage in any part-time work or business while schooling": "part_time_work",
    "do you engage in part-time work or business while schooling": "part_time_work",
    "part-time work or business while schooling": "part_time_work",
    "part time work": "part_time_work",
    "part-time work": "part_time_work",
    "how far do you live from your campus": "distance",
    "how far do you live from campus": "distance",
    "distance from campus": "distance",
    "distance": "distance",
    "how stable is your internet access": "internet_access",
    "how stable is your internet access for studying": "internet_access",
    "internet access for studying": "internet_access",
    "internet access": "internet_access",
    "do you engage in extracurricular activities": "extracurricular",
    "extracurricular activities": "extracurricular",
    "extracurricular": "extracurricular",
    "how much do your family responsibilities affect your studies": "family_responsibilities",
    "how much do family responsibilities affect your study time": "family_responsibilities",
    "family responsibilities affect your study time": "family_responsibilities",
    "family responsibilities": "family_responsibilities",
    "how would you rate your mental health and stress level as a student": "stress_level",
    "how would you rate your mental health and stress level": "stress_level",
    "mental health and stress level": "stress_level",
    "stress level": "stress_level",
    "are you studying your current course out of personal interest": "course_interest",
    "studying your current course out of personal interest": "course_interest",
    "course interest": "course_interest",
    "how would you rate your overall motivation to succeed academically": "motivation",
    "overall motivation to succeed academically": "motivation",
    "motivation": "motivation",
    "how would you rate your own academic performance overall": "self_rated_perf",
    "own academic performance overall": "self_rated_perf",
    "self rated performance": "self_rated_perf",
    "self-rated performance": "self_rated_perf",
    "self_rated_perf": "self_rated_perf",
}

VALUE_MAP: dict[str, dict[str, str]] = {
    "gender": {
        "male": "Male", "female": "Female",
        "prefer not to say": "Prefer not to say",
    },
    "age_range": {
        "16 \u2013 19": "16-19", "16-19": "16-19", "16 - 19": "16-19",
        "20 \u2013 23": "20-23", "20-23": "20-23", "20 - 23": "20-23",
        "24 \u2013 27": "24-27", "24-27": "24-27", "24 - 27": "24-27",
        "28 and above": "28+", "28+": "28+",
    },
    "level": {
        "100 level": "100", "100": "100",
        "200 level": "200", "200": "200",
        "300 level": "300", "300": "300",
        "400 level": "400", "400": "400",
        "500 level": "500", "500": "500",
        "600 level": "500",
    },
    "current_cgpa": {
        "4.5 \u2013 5.0 (first class)": "First Class (4.5-5.0)",
        "4.5 - 5.0 (first class)": "First Class (4.5-5.0)",
        "first class (4.5-5.0)": "First Class (4.5-5.0)",
        "first class": "First Class (4.5-5.0)",
        "3.5 \u2013 4.4 (second class upper)": "Second Class Upper (3.5-4.4)",
        "3.5 - 4.4 (second class upper)": "Second Class Upper (3.5-4.4)",
        "second class upper (3.5-4.4)": "Second Class Upper (3.5-4.4)",
        "second class upper": "Second Class Upper (3.5-4.4)",
        "2.5 \u2013 3.4 (second class lower)": "Second Class Lower (2.5-3.4)",
        "2.5 - 3.4 (second class lower)": "Second Class Lower (2.5-3.4)",
        "second class lower (2.5-3.4)": "Second Class Lower (2.5-3.4)",
        "second class lower": "Second Class Lower (2.5-3.4)",
        "1.5 \u2013 2.4 (third class)": "Third Class (1.5-2.4)",
        "1.5 - 2.4 (third class)": "Third Class (1.5-2.4)",
        "third class (1.5-2.4)": "Third Class (1.5-2.4)",
        "third class": "Third Class (1.5-2.4)",
        "below 1.5 / not sure": "Below 1.5",
        "below 1.5": "Below 1.5",
        "not sure": "Below 1.5",
    },
    "courses_failed": {
        "none": "None",
        "1 \u2013 2": "1-2", "1 - 2": "1-2", "1-2": "1-2",
        "3 \u2013 5": "3-5", "3 - 5": "3-5", "3-5": "3-5",
        "more than 5": "More than 5",
    },
    "father_education": {
        "no formal education": "No formal education",
        "primary school": "Primary", "primary": "Primary",
        "secondary school": "Secondary", "secondary": "Secondary",
        "ond / nce": "OND/NCE", "ond/nce": "OND/NCE",
        "ond": "OND/NCE", "nce": "OND/NCE",
        "bachelor's degree": "Bachelor's degree", "bsc": "Bachelor's degree",
        "postgraduate (msc / phd)": "Postgraduate", "postgraduate": "Postgraduate",
        "msc": "Postgraduate", "phd": "Postgraduate",
    },
    "mother_education": {
        "no formal education": "No formal education",
        "primary school": "Primary", "primary": "Primary",
        "secondary school": "Secondary", "secondary": "Secondary",
        "ond / nce": "OND/NCE", "ond/nce": "OND/NCE",
        "ond": "OND/NCE", "nce": "OND/NCE",
        "bachelor's degree": "Bachelor's degree", "bsc": "Bachelor's degree",
        "postgraduate (msc / phd)": "Postgraduate", "postgraduate": "Postgraduate",
        "msc": "Postgraduate", "phd": "Postgraduate",
    },
    "family_income": {
        "below \u20a650,000": "Below \u20a650,000",
        "below n50,000": "Below \u20a650,000",
        "\u20a650,000 \u2013 \u20a6150,000": "\u20a650,000-\u20a6150,000",
        "n50,000 - n150,000": "\u20a650,000-\u20a6150,000",
        "\u20a6150,000 \u2013 \u20a6300,000": "\u20a6150,000-\u20a6300,000",
        "n150,000 - n300,000": "\u20a6150,000-\u20a6300,000",
        "\u20a6300,000 \u2013 \u20a6500,000": "\u20a6300,000-\u20a6500,000",
        "n300,000 - n500,000": "\u20a6300,000-\u20a6500,000",
        "above \u20a6500,000": "Above \u20a6500,000",
        "above n500,000": "Above \u20a6500,000",
    },
    "household_size": {
        "1 \u2013 3": "1-3", "1 - 3": "1-3", "1-3": "1-3",
        "4 \u2013 6": "4-6", "4 - 6": "4-6", "4-6": "4-6",
        "7 \u2013 10": "7-10", "7 - 10": "7-10", "7-10": "7-10",
        "more than 10": "More than 10",
    },
    "parental_involvement": {
        "very involved \u2014 they follow up regularly": "Very involved",
        "very involved - they follow up regularly": "Very involved",
        "very involved": "Very involved",
        "somewhat involved": "Somewhat involved",
        "not involved at all": "Not involved",
        "not involved": "Not involved",
    },
    "study_hours": {
        "less than 1 hour": "Less than 1 hour",
        "1 \u2013 2 hours": "1-2 hours", "1 - 2 hours": "1-2 hours", "1-2 hours": "1-2 hours",
        "3 \u2013 4 hours": "3-4 hours", "3 - 4 hours": "3-4 hours", "3-4 hours": "3-4 hours",
        "more than 4 hours": "More than 4 hours",
    },
    "attendance": {
        "always (90\u2013100%)": "Always (90-100%)",
        "always (90 \u2013 100%)": "Always (90-100%)",
        "always (90-100%)": "Always (90-100%)",
        "always": "Always (90-100%)",
        "often (70\u201389%)": "Often (70-89%)",
        "often (70 \u2013 89%)": "Often (70-89%)",
        "often (70-89%)": "Often (70-89%)",
        "often": "Often (70-89%)",
        "sometimes (50\u201369%)": "Sometimes (50-69%)",
        "sometimes (50 \u2013 69%)": "Sometimes (50-69%)",
        "sometimes (50-69%)": "Sometimes (50-69%)",
        "sometimes": "Sometimes (50-69%)",
        "rarely (below 50%)": "Rarely (<50%)",
        "rarely (<50%)": "Rarely (<50%)",
        "rarely": "Rarely (<50%)",
    },
    "class_prep": {
        "always": "Always", "sometimes": "Sometimes",
        "rarely": "Rarely", "never": "Never",
    },
    "resource_use": {
        "very often": "Very often", "sometimes": "Sometimes",
        "rarely": "Rarely", "never": "Never",
    },
    "sleep_hours": {
        "less than 4 hours": "Less than 4 hours",
        "4 \u2013 6 hours": "4-6 hours", "4 - 6 hours": "4-6 hours", "4-6 hours": "4-6 hours",
        "6 \u2013 8 hours": "6-8 hours", "6 - 8 hours": "6-8 hours", "6-8 hours": "6-8 hours",
        "more than 8 hours": "More than 8 hours",
    },
    "group_study": {
        "yes, regularly": "Yes regularly", "yes regularly": "Yes regularly",
        "occasionally": "Occasionally",
        "no": "No",
    },
    "past_questions": {
        "always before exams": "Always before exams",
        "sometimes": "Sometimes",
        "rarely": "Rarely",
        "never": "Never",
    },
    "part_time_work": {
        "yes, regularly (more than 3 days a week)": "Yes regularly",
        "yes regularly": "Yes regularly", "yes - regularly": "Yes regularly",
        "occasionally (1 \u2013 2 days a week)": "Occasionally",
        "occasionally (1 - 2 days a week)": "Occasionally",
        "occasionally": "Occasionally",
        "no": "No",
    },
    "distance": {
        "on campus": "On campus",
        "less than 30 minutes away": "Less than 30 mins",
        "less than 30 minutes": "Less than 30 mins",
        "less than 30 mins": "Less than 30 mins",
        "30 minutes \u2013 1 hour away": "30 mins-1 hour",
        "30 minutes - 1 hour away": "30 mins-1 hour",
        "30 minutes \u2013 1 hour": "30 mins-1 hour",
        "30 mins-1 hour": "30 mins-1 hour",
        "more than 1 hour away": "More than 1 hour",
        "more than 1 hour": "More than 1 hour",
    },
    "internet_access": {
        "very stable": "Very stable",
        "mostly stable": "Mostly stable",
        "unstable": "Unstable",
        "i rarely have internet access": "Rarely have access",
        "i rarely have access": "Rarely have access",
        "rarely have access": "Rarely have access",
    },
    "extracurricular": {
        "yes, heavily involved": "Yes heavily involved",
        "yes heavily involved": "Yes heavily involved",
        "occasionally": "Occasionally",
        "no": "No",
    },
    "family_responsibilities": {
        "not at all": "Not at all",
        "slightly": "Slightly",
        "moderately": "Moderately",
        "significantly": "Significantly",
    },
    "stress_level": {
        "low \u2014 i cope very well": "Low", "low - i cope very well": "Low",
        "low": "Low",
        "moderate \u2014 manageable": "Moderate", "moderate - manageable": "Moderate",
        "moderate": "Moderate",
        "high \u2014 it affects my studies": "High", "high - it affects my studies": "High",
        "high": "High",
        "very high \u2014 i struggle regularly": "Very high",
        "very high - i struggle regularly": "Very high",
        "very high": "Very high",
    },
    "course_interest": {
        "yes, it's my passion": "Yes my passion",
        "yes my passion": "Yes my passion",
        "partially \u2014 some interest": "Partially interested",
        "partially - some interest": "Partially interested",
        "partially interested": "Partially interested",
        "no \u2014 it was parental/family pressure": "No - family pressure",
        "no - it was parental/family pressure": "No - family pressure",
        "no - family pressure": "No - family pressure",
        "no \u2014 i had no other choice": "No - no other choice",
        "no - i had no other choice": "No - no other choice",
        "no - no other choice": "No - no other choice",
    },
    "motivation": {
        "very high": "Very high", "high": "High",
        "moderate": "Moderate", "low": "Low",
    },
    "self_rated_perf": {
        "excellent": "Excellent", "good": "Good", "average": "Average",
        "poor": "Poor", "very poor": "Very Poor",
    },
}

CGPA_TO_PERFORMANCE: dict[str, str] = {
    "First Class (4.5-5.0)": "First Class (4.5-5.0)",
    "Second Class Upper (3.5-4.4)": "Second Class Upper (3.5-4.4)",
    "Second Class Lower (2.5-3.4)": "Second Class Lower (2.5-3.4)",
    "Third Class (1.5-2.4)": "Third Class (1.5-2.4)",
    "Below 1.5": "Below Third Class (<1.5)",
}


def _normalise_header(raw: str) -> str:
    return raw.strip().lower().rstrip("?").strip()


def map_columns(headers: list[str]) -> dict[str, str]:
    """Return {original_header: feature_name} for recognised columns."""
    mapping: dict[str, str] = {}
    for h in headers:
        key = _normalise_header(h)
        if key in COLUMN_MAP:
            mapping[h] = COLUMN_MAP[key]
        else:
            for pattern, feature in COLUMN_MAP.items():
                if pattern in key or key in pattern:
                    mapping[h] = feature
                    break
    return mapping


def normalise_value(feature: str, raw_value: str) -> str | None:
    """Map a raw Google Form cell value to the canonical category value.
    Returns None if no match found.
    """
    vm = VALUE_MAP.get(feature, {})
    key = raw_value.strip().lower()
    if key in vm:
        return vm[key]
    for pattern, canonical in vm.items():
        if pattern in key or key in pattern:
            return canonical
    allowed = CATEGORIES.get(feature, [])
    for a in allowed:
        if a.lower() == key:
            return a
    return None
