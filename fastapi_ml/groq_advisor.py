"""AI academic-advisor integration powered by Groq.

Uses the Groq Python SDK. If GROQ_API_KEY is not configured, or the API call
fails, a deterministic rule-based recommendation is returned so the prediction
pipeline remains fully functional without external dependencies.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("acadpredict.groq_advisor")

GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def _build_prompt(
    student_data: dict,
    predicted_class: str,
    confidence: float,
    estimated_cgpa: float,
) -> str:
    return f"""
You are an academic advisor at a Nigerian university.
A student has been predicted to finish this semester in the {predicted_class}
range (estimated CGPA: {estimated_cgpa:.2f}) with {confidence:.0%} model confidence.

Student survey profile:
- Current CGPA band: {student_data.get('current_cgpa')}
- Study hours per day: {student_data.get('study_hours')}
- Lecture attendance: {student_data.get('attendance')}
- Prepares before class: {student_data.get('class_prep')}
- Uses academic resources: {student_data.get('resource_use')}
- Practises past questions: {student_data.get('past_questions')}
- Group study: {student_data.get('group_study')}
- Courses failed/carried over: {student_data.get('courses_failed')}
- Sleep hours per night: {student_data.get('sleep_hours')}
- Academic motivation: {student_data.get('motivation')}
- Stress level: {student_data.get('stress_level')}
- Course interest: {student_data.get('course_interest')}
- Part-time work: {student_data.get('part_time_work')}
- Family responsibilities impact: {student_data.get('family_responsibilities')}
- Internet access: {student_data.get('internet_access')}
- Distance from campus: {student_data.get('distance')}

Provide exactly 3 numbered, specific, actionable academic intervention
recommendations to help this student improve or maintain their CGPA.
Write in plain English. Maximum 200 words total.
Do not use emojis. Do not repeat the student data back.
Be empathetic but direct. Reference the CGPA target where relevant.
""".strip()


def _fallback_recommendation(
    student_data: dict,
    predicted_class: str,
    confidence: float,
    estimated_cgpa: float,
) -> str:
    tips: list[str] = []

    if student_data.get("attendance") in {"Sometimes (50-69%)", "Rarely (<50%)"}:
        tips.append(
            "Commit to attending at least 90% of lectures. Consistent attendance "
            "is directly tied to understanding coursework and performing well in exams."
        )
    if student_data.get("study_hours") in {"Less than 1 hour", "1-2 hours"}:
        tips.append(
            "Increase focused study to 3-4 hours daily using timed sessions. "
            "Prioritise courses you have previously struggled with."
        )
    if student_data.get("courses_failed") in {"3-5", "More than 5"}:
        tips.append(
            "Meet your course adviser this week to plan deliberate retakes of "
            "carried-over courses and avoid overloading your semester."
        )
    if student_data.get("class_prep") in {"Rarely", "Never"}:
        tips.append(
            "Read ahead before each lecture — even 20 minutes of preparation helps "
            "you absorb material faster and ask better questions in class."
        )
    if student_data.get("past_questions") in {"Rarely", "Never"}:
        tips.append(
            "Practice past exam questions consistently. It is the most reliable "
            "way to understand exam patterns and close knowledge gaps."
        )
    if student_data.get("stress_level") in {"High", "Very high"} or \
       student_data.get("sleep_hours") in {"Less than 4 hours", "4-6 hours"}:
        tips.append(
            "Protect 7-8 hours of sleep nightly and use the campus counselling "
            "service to build stress-management routines before exam season."
        )
    if student_data.get("motivation") in {"Low", "Moderate"}:
        tips.append(
            "Set a specific CGPA target for this semester and break it into weekly "
            "course goals. Tracking small wins builds sustained motivation."
        )

    defaults = [
        "Join or form a small study group to stay accountable and clarify difficult topics together.",
        "Book regular consultations with your lecturers during their office hours.",
        "Use Google Scholar, YouTube tutorials, and past questions to supplement your notes.",
    ]
    for tip in defaults:
        if len(tips) >= 3:
            break
        tips.append(tip)

    chosen = tips[:3]
    numbered = "\n".join(f"{i}. {tip}" for i, tip in enumerate(chosen, start=1))
    header = (
        f"Predicted end-of-session outcome: {predicted_class} "
        f"(est. CGPA {estimated_cgpa:.2f}, {confidence:.0%} confidence).\n\n"
        "Three focused steps to improve or maintain your standing:\n"
    )
    return header + numbered


def generate_recommendation(
    student_data: dict,
    predicted_class: str,
    confidence: float,
    estimated_cgpa: float = 2.95,
) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set; using rule-based fallback.")
        return _fallback_recommendation(
            student_data, predicted_class, confidence, estimated_cgpa
        )

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        prompt = _build_prompt(student_data, predicted_class, confidence, estimated_cgpa)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=350,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        logger.exception("Groq request failed; using fallback: %s", exc)
        return _fallback_recommendation(
            student_data, predicted_class, confidence, estimated_cgpa
        )
