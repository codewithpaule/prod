"""Trainer for Google Form survey exports (responses.csv).

Parses real survey responses and retrains the model on that data only.
Synthetic blending is optional and off by default.

Run:  python -m ml.train_from_real_data                    (from fastapi_ml/)
Or:   python -m ml.train_from_real_data ../responses.csv
"""
from __future__ import annotations

import csv
import io
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
DEFAULT_CSV = REPO_ROOT / "responses.csv"

COL_TO_FEATURE: dict[str, str] = {
    "what is your gender": "gender",
    "what is your age range": "age_range",
    "what level are you currently in": "level",
    "what is your current cgpa range": "current_cgpa",
    "how many courses have you failed or are carrying over": "courses_failed",
    "what is your father's highest level of education": "father_education",
    "what is your mother's highest level of education": "mother_education",
    "what is your family's approximate monthly income level": "family_income",
    "how many people are financially dependent in your household": "household_size",
    "how involved are your parents/guardians in your academic progress": "parental_involvement",
    "on average, how many hours do you spend studying per day": "study_hours",
    "how often do you attend lectures": "attendance",
    "how often do you read ahead before class": "class_prep",
    "how often do you use academic resources": "resource_use",
    "how many hours do you sleep on average per night": "sleep_hours",
    "do you participate actively in group study or discussions": "group_study",
    "how often do you practice past exam questions": "past_questions",
    "do you engage in any part-time work or business while schooling": "part_time_work",
    "how far do you live from your campus": "distance",
    "how stable is your internet access": "internet_access",
    "do you engage in extracurricular activities": "extracurricular",
    "how much do your family responsibilities affect your studies": "family_responsibilities",
    "how would you rate your mental health and stress level": "stress_level",
    "are you studying your current course out of personal interest": "course_interest",
    "how would you rate your overall motivation to succeed academically": "motivation",
    "how would you rate your own academic performance overall": "self_rated_perf",
}

VALUE_MAP: dict[str, dict[str, str]] = {
    "gender": {
        "female": "Female", "male": "Male",
        "prefer not to say": "Prefer not to say",
    },
    "age_range": {
        "16 \u2013 19": "16-19", "16-19": "16-19",
        "20 \u2013 23": "20-23", "20-23": "20-23",
        "24 \u2013 27": "24-27", "24-27": "24-27",
        "28 and above": "28+", "28+": "28+",
    },
    "level": {
        "100 level": "100", "200 level": "200", "300 level": "300",
        "400 level": "400", "500 level": "500",
        "600 level": "500",
    },
    "current_cgpa": {
        "4.5 \u2013 5.0 (first class)": "First Class (4.5-5.0)",
        "3.5 \u2013 4.4 (second class upper)": "Second Class Upper (3.5-4.4)",
        "2.5 \u2013 3.4 (second class lower)": "Second Class Lower (2.5-3.4)",
        "1.5 \u2013 2.4 (third class)": "Third Class (1.5-2.4)",
        "below 1.5 / not sure": "Below 1.5",
        "below 1.5": "Below 1.5",
    },
    "courses_failed": {
        "none": "None",
        "1 \u2013 2": "1-2", "1-2": "1-2",
        "3 \u2013 5": "3-5", "3-5": "3-5",
        "more than 5": "More than 5",
    },
    "father_education": {
        "no formal education": "No formal education",
        "primary school": "Primary", "primary": "Primary",
        "secondary school": "Secondary", "secondary": "Secondary",
        "ond / nce": "OND/NCE", "ond/nce": "OND/NCE",
        "bachelor's degree": "Bachelor's degree",
        "postgraduate (msc / phd)": "Postgraduate",
        "postgraduate": "Postgraduate",
    },
    "mother_education": {
        "no formal education": "No formal education",
        "primary school": "Primary", "primary": "Primary",
        "secondary school": "Secondary", "secondary": "Secondary",
        "ond / nce": "OND/NCE", "ond/nce": "OND/NCE",
        "bachelor's degree": "Bachelor's degree",
        "postgraduate (msc / phd)": "Postgraduate",
        "postgraduate": "Postgraduate",
    },
    "family_income": {
        "below \u20a650,000": "Below \u20a650,000",
        "\u20a650,000 \u2013 \u20a6150,000": "\u20a650,000-\u20a6150,000",
        "\u20a6150,000 \u2013 \u20a6300,000": "\u20a6150,000-\u20a6300,000",
        "\u20a6300,000 \u2013 \u20a6500,000": "\u20a6300,000-\u20a6500,000",
        "above \u20a6500,000": "Above \u20a6500,000",
        "below n50,000": "Below \u20a650,000",
    },
    "household_size": {
        "1 \u2013 3": "1-3", "1-3": "1-3",
        "4 \u2013 6": "4-6", "4-6": "4-6",
        "7 \u2013 10": "7-10", "7-10": "7-10",
        "more than 10": "More than 10",
    },
    "parental_involvement": {
        "very involved \u2014 they follow up regularly": "Very involved",
        "very involved": "Very involved",
        "somewhat involved": "Somewhat involved",
        "not involved at all": "Not involved",
        "not involved": "Not involved",
    },
    "study_hours": {
        "less than 1 hour": "Less than 1 hour",
        "1 \u2013 2 hours": "1-2 hours", "1-2 hours": "1-2 hours",
        "3 \u2013 4 hours": "3-4 hours", "3-4 hours": "3-4 hours",
        "more than 4 hours": "More than 4 hours",
    },
    "attendance": {
        "always (90\u2013100%)": "Always (90-100%)",
        "always (90-100%)": "Always (90-100%)",
        "often (70\u201389%)": "Often (70-89%)",
        "often (70-89%)": "Often (70-89%)",
        "sometimes (50\u201369%)": "Sometimes (50-69%)",
        "sometimes (50-69%)": "Sometimes (50-69%)",
        "rarely (below 50%)": "Rarely (<50%)",
        "rarely (<50%)": "Rarely (<50%)",
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
        "4 \u2013 6 hours": "4-6 hours", "4-6 hours": "4-6 hours",
        "6 \u2013 8 hours": "6-8 hours", "6-8 hours": "6-8 hours",
        "more than 8 hours": "More than 8 hours",
    },
    "group_study": {
        "yes, regularly": "Yes regularly",
        "yes regularly": "Yes regularly",
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
        "yes regularly": "Yes regularly",
        "occasionally (1 \u2013 2 days a week)": "Occasionally",
        "occasionally": "Occasionally",
        "no": "No",
    },
    "distance": {
        "on campus": "On campus",
        "less than 30 minutes away": "Less than 30 mins",
        "less than 30 mins": "Less than 30 mins",
        "30 minutes \u2013 1 hour away": "30 mins-1 hour",
        "30 mins-1 hour": "30 mins-1 hour",
        "more than 1 hour away": "More than 1 hour",
        "more than 1 hour": "More than 1 hour",
    },
    "internet_access": {
        "very stable": "Very stable",
        "mostly stable": "Mostly stable",
        "unstable": "Unstable",
        "i rarely have internet access": "Rarely have access",
        "rarely have access": "Rarely have access",
    },
    "extracurricular": {
        "yes, heavily involved": "Yes heavily involved",
        "yes heavily involved": "Yes heavily involved",
        "occasionally": "Occasionally",
        "no": "No",
    },
    "family_responsibilities": {
        "not at all": "Not at all", "slightly": "Slightly",
        "moderately": "Moderately", "significantly": "Significantly",
    },
    "stress_level": {
        "low \u2014 i cope very well": "Low",
        "low": "Low",
        "moderate \u2014 manageable": "Moderate",
        "moderate": "Moderate",
        "high \u2014 it affects my studies": "High",
        "high": "High",
        "very high \u2014 i struggle regularly": "Very high",
        "very high": "Very high",
    },
    "course_interest": {
        "yes, it's my passion": "Yes my passion",
        "yes my passion": "Yes my passion",
        "partially \u2014 some interest": "Partially interested",
        "partially interested": "Partially interested",
        "no \u2014 it was parental/family pressure": "No - family pressure",
        "no - family pressure": "No - family pressure",
        "no \u2014 i had no other choice": "No - no other choice",
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

CGPA_TO_CLASS: dict[str, str] = {
    "First Class (4.5-5.0)": "First Class (4.5-5.0)",
    "Second Class Upper (3.5-4.4)": "Second Class Upper (3.5-4.4)",
    "Second Class Lower (2.5-3.4)": "Second Class Lower (2.5-3.4)",
    "Third Class (1.5-2.4)": "Third Class (1.5-2.4)",
    "Below 1.5": "Below Third Class (<1.5)",
}


def _norm_col(h: str) -> str:
    return h.strip().lower().rstrip("?").strip()


def _read_csv_text(csv_path: Path) -> str:
    """Read a plain CSV or a zip archive containing a CSV (Google Form export)."""
    raw = csv_path.read_bytes()
    if raw[:2] == b"PK":
        with zipfile.ZipFile(io.BytesIO(raw)) as zf:
            for name in zf.namelist():
                if name.lower().endswith(".csv"):
                    return zf.read(name).decode("utf-8-sig", errors="replace")
        raise ValueError(f"No CSV found inside zip archive: {csv_path}")
    return raw.decode("utf-8-sig", errors="replace")


def parse_csv(csv_path: Path) -> tuple[list[dict], list[str]]:
    rows: list[dict] = []
    skipped: list[str] = []

    csv_text = _read_csv_text(csv_path)
    reader = csv.DictReader(io.StringIO(csv_text))
    for i, raw_row in enumerate(reader, start=2):
        features: dict[str, str] = {}
        row_issues: list[str] = []

        for col, raw_val in raw_row.items():
            norm_col = _norm_col(col)
            feature = None
            for pattern, feat in COL_TO_FEATURE.items():
                if pattern in norm_col:
                    feature = feat
                    break
            if feature is None:
                continue

            raw_val = (raw_val or "").strip()
            if not raw_val:
                continue

            vm = VALUE_MAP.get(feature, {})
            canonical = vm.get(raw_val.lower())
            if canonical is None:
                for k, v in vm.items():
                    if k in raw_val.lower() or raw_val.lower() in k:
                        canonical = v
                        break
            if canonical is None:
                row_issues.append(f"{feature}='{raw_val}'")
            else:
                features[feature] = canonical

        if len(features) < 15:
            skipped.append(f"Row {i}: only {len(features)} features mapped, skipping.")
            continue

        cgpa_val = features.get("current_cgpa")
        label = CGPA_TO_CLASS.get(cgpa_val, "") if cgpa_val else ""
        if not label:
            skipped.append(f"Row {i}: could not determine class label, skipping.")
            continue

        if row_issues:
            skipped.append(f"Row {i}: unmapped values for {', '.join(row_issues[:3])}.")

        rows.append({"features": features, "label": label})

    return rows, skipped


def main(csv_path: Path | None = None, use_synthetic: bool = False, synthetic_n: int = 3000) -> None:
    from ml.train_model import train_with_real_data

    path = csv_path or DEFAULT_CSV
    if not path.exists():
        print(f"ERROR: Training file not found: {path}")
        sys.exit(1)

    print(f"Parsing {path} …")
    rows, skipped = parse_csv(path)
    print(f"Valid rows: {len(rows)}, skipped: {len(skipped)}")
    for s in skipped:
        print(f"  SKIP: {s}")

    if not rows:
        print("ERROR: No valid rows to train on.")
        sys.exit(1)

    real_rows = []
    for r in rows:
        row = dict(r["features"])
        row["performance_class"] = r["label"]
        real_rows.append(row)

    if use_synthetic:
        print(f"\nTraining with {len(real_rows)} real rows + {synthetic_n} synthetic rows …")
    else:
        print(f"\nTraining with {len(real_rows)} real rows only …")

    accuracy, total, bias = train_with_real_data(
        real_rows, use_synthetic=use_synthetic, synthetic_n=synthetic_n
    )
    print(f"\nDone. Total rows used: {total}, Validation accuracy: {accuracy:.1%}")
    flags = bias.get("flags", [])
    if flags:
        print("Bias flags:")
        for f in flags:
            print(f"  {f}")
    else:
        print("No bias flags detected.")


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    main(path)
