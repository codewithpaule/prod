"""AI academic-advisor integration powered by Groq.

Replaces the original Anthropic Claude integration. Uses the Groq Python SDK
(OpenAI-compatible chat completions). If ``GROQ_API_KEY`` is not configured, or
the API call fails, a deterministic rule-based recommendation is returned so the
prediction pipeline remains fully functional without external dependencies.
"""
from __future__ import annotations

import logging
import os

logger = logging.getLogger("acadpredict.groq_advisor")

# A fast, high-quality general model available on Groq.
GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")


def _build_prompt(student_data: dict, predicted_class: str, confidence: float) -> str:
    return f"""
    You are an academic advisor at a Nigerian university.
    A student has been classified as {predicted_class}
    with {confidence:.0%} model confidence.

    Student profile:
    - Study hours per day: {student_data.get('study_hours')}
    - Lecture attendance: {student_data.get('attendance')}
    - Courses failed/carried over: {student_data.get('courses_failed')}
    - Financial stress level: {student_data.get('financial_stress')}
    - Sleep hours per night: {student_data.get('sleep_hours')}
    - Academic motivation: {student_data.get('motivation')}
    - Mother education level: {student_data.get('mother_education')}
    - Part-time work: {student_data.get('part_time_work')}
    - Stress level: {student_data.get('stress_level')}

    Provide exactly 3 numbered, specific, actionable academic
    intervention recommendations for this student.
    Write in plain English. Maximum 180 words total.
    Do not use emojis. Do not repeat the student data back.
    Be empathetic but direct.
    """


def _fallback_recommendation(student_data: dict, predicted_class: str, confidence: float) -> str:
    """Deterministic recommendation used when Groq is unavailable."""
    tips: list[str] = []

    if student_data.get("attendance") in {"<50%", "50-70%"}:
        tips.append(
            "Commit to attending at least 90% of lectures; arrange to copy notes "
            "for any unavoidable absences and review them within 24 hours."
        )
    if student_data.get("study_hours") in {"<1 hour", "1-2 hours"}:
        tips.append(
            "Increase focused study to 3-4 hours daily using short timed sessions, "
            "prioritising the courses you have previously struggled with."
        )
    if student_data.get("courses_failed") in {"3-4", "5+"}:
        tips.append(
            "Meet your course adviser this week to plan deliberate retakes of carried-over "
            "courses and avoid overloading your semester."
        )
    if student_data.get("financial_stress") in {"Moderate", "High"}:
        tips.append(
            "Speak to the student affairs or bursary office about bursaries, work-study, "
            "or payment plans to reduce financial pressure on your studies."
        )
    if student_data.get("stress_level") in {"High", "Severe"} or student_data.get("sleep_hours") in {"<4 hours", "4-6 hours"}:
        tips.append(
            "Protect 7-8 hours of sleep and use the campus counselling service to build "
            "stress-management routines that keep you steady through exams."
        )

    defaults = [
        "Form or join a small study group to stay accountable and clarify difficult topics.",
        "Set specific weekly academic goals and review your progress every weekend.",
        "Book regular consultations with your lecturers during their office hours.",
    ]
    for tip in defaults:
        if len(tips) >= 3:
            break
        tips.append(tip)

    chosen = tips[:3]
    numbered = "\n".join(f"{i}. {tip}" for i, tip in enumerate(chosen, start=1))
    header = (
        f"Based on a {predicted_class} classification ({confidence:.0%} confidence), "
        "here are three focused steps:\n"
    )
    return header + numbered


def generate_recommendation(
    student_data: dict, predicted_class: str, confidence: float
) -> str:
    """Generate a 3-point academic recommendation using Groq, with a safe fallback."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        logger.warning("GROQ_API_KEY not set; using rule-based fallback recommendation.")
        return _fallback_recommendation(student_data, predicted_class, confidence)

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        prompt = _build_prompt(student_data, predicted_class, confidence)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            max_tokens=300,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:  # pragma: no cover - network dependent
        logger.exception("Groq request failed; using fallback recommendation: %s", exc)
        return _fallback_recommendation(student_data, predicted_class, confidence)
