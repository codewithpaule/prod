"""Train and compare models for AcadPredict AI.

Generates a realistic synthetic dataset of Nigerian university students, then
optionally blends with real survey rows uploaded by the admin. Trains four
classifiers and persists the best-performing Random Forest to ``model.pkl``.

Run:  python -m ml.train_model   (from the fastapi_ml/ directory)
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

try:
    from imblearn.over_sampling import SMOTE
    HAS_SMOTE = True
except Exception:
    HAS_SMOTE = False

from ml.categories import CATEGORIES, PERFORMANCE_CLASSES, CGPA_MIDPOINTS

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "model.pkl"
PREPROCESSOR_PATH = HERE / "preprocessor.pkl"
FEATURE_IMPORTANCE_PATH = HERE / "feature_importance.json"

FEATURES = list(CATEGORIES.keys())
RNG = np.random.default_rng(42)

SCORE_WEIGHTS: dict[str, dict[str, float]] = {
    "current_cgpa": {
        "First Class (4.5-5.0)": 6.0,
        "Second Class Upper (3.5-4.4)": 2.5,
        "Second Class Lower (2.5-3.4)": -0.5,
        "Third Class (1.5-2.4)": -3.0,
        "Below 1.5": -6.0,
    },
    "courses_failed": {
        "None": 2.0, "1-2": 0.5, "3-5": -1.5, "More than 5": -3.0,
    },
    "study_hours": {
        "Less than 1 hour": -2.0, "1-2 hours": -0.5,
        "3-4 hours": 1.5, "More than 4 hours": 2.5,
    },
    "attendance": {
        "Always (90-100%)": 2.5, "Often (70-89%)": 1.0,
        "Sometimes (50-69%)": -0.5, "Rarely (<50%)": -2.5,
    },
    "motivation": {
        "Very high": 2.5, "High": 1.5, "Moderate": 0.0, "Low": -2.0,
    },
    "self_rated_perf": {
        "Excellent": 2.5, "Good": 1.0, "Average": -0.5,
        "Poor": -1.5, "Very Poor": -2.5,
    },
    "stress_level": {
        "Low": 1.0, "Moderate": 0.2, "High": -1.0, "Very high": -2.0,
    },
    "class_prep": {
        "Always": 2.0, "Sometimes": 0.5, "Rarely": -0.5, "Never": -1.5,
    },
    "resource_use": {
        "Very often": 1.5, "Sometimes": 0.5, "Rarely": -0.5, "Never": -1.0,
    },
    "past_questions": {
        "Always before exams": 2.0, "Sometimes": 0.5,
        "Rarely": -0.5, "Never": -1.0,
    },
    "group_study": {
        "Yes regularly": 1.0, "Occasionally": 0.3, "No": -0.3,
    },
    "sleep_hours": {
        "Less than 4 hours": -1.5, "4-6 hours": 0.0,
        "6-8 hours": 1.5, "More than 8 hours": 0.3,
    },
    "parental_involvement": {
        "Very involved": 1.0, "Somewhat involved": 0.3, "Not involved": -0.5,
    },
    "course_interest": {
        "Yes my passion": 1.5, "Partially interested": 0.3,
        "No - family pressure": -0.8, "No - no other choice": -1.2,
    },
    "part_time_work": {
        "No": 0.5, "Occasionally": -0.2, "Yes regularly": -1.0,
    },
    "family_responsibilities": {
        "Not at all": 0.5, "Slightly": 0.0, "Moderately": -0.5,
        "Significantly": -1.5,
    },
    "internet_access": {
        "Very stable": 0.8, "Mostly stable": 0.3,
        "Unstable": -0.3, "Rarely have access": -0.8,
    },
    "distance": {
        "On campus": 0.5, "Less than 30 mins": 0.3,
        "30 mins-1 hour": -0.2, "More than 1 hour": -0.8,
    },
    "extracurricular": {
        "Yes heavily involved": -0.3, "Occasionally": 0.3, "No": 0.0,
    },
    "father_education": {
        "No formal education": -0.5, "Primary": -0.3, "Secondary": 0.0,
        "OND/NCE": 0.3, "Bachelor's degree": 0.6, "Postgraduate": 1.0,
    },
    "mother_education": {
        "No formal education": -0.5, "Primary": -0.3, "Secondary": 0.0,
        "OND/NCE": 0.3, "Bachelor's degree": 0.6, "Postgraduate": 1.0,
    },
    "family_income": {
        "Below \u20a650,000": -1.0,
        "\u20a650,000-\u20a6150,000": -0.3,
        "\u20a6150,000-\u20a6300,000": 0.2,
        "\u20a6300,000-\u20a6500,000": 0.6,
        "Above \u20a6500,000": 1.0,
    },
    "household_size": {
        "1-3": 0.5, "4-6": 0.0, "7-10": -0.5, "More than 10": -1.0,
    },
}


def _cgpa_from_score(score: float) -> float:
    base = 3.0 + 0.12 * score
    noise = RNG.normal(0.0, 0.35)
    return float(np.clip(base + noise, 0.0, 5.0))


def _class_from_cgpa(cgpa: float) -> str:
    if cgpa >= 4.5:
        return "First Class (4.5-5.0)"
    if cgpa >= 3.5:
        return "Second Class Upper (3.5-4.4)"
    if cgpa >= 2.5:
        return "Second Class Lower (2.5-3.4)"
    if cgpa >= 1.5:
        return "Third Class (1.5-2.4)"
    return "Below Third Class (<1.5)"


def generate_synthetic_data(n: int = 4000) -> pd.DataFrame:
    rows: list[dict] = []
    for _ in range(n):
        row: dict = {
            feature: str(RNG.choice(options))
            for feature, options in CATEGORIES.items()
        }
        score = sum(
            SCORE_WEIGHTS.get(feature, {}).get(str(row[feature]), 0.0)
            for feature in FEATURES
        )
        cgpa = _cgpa_from_score(score)
        row["cgpa"] = cgpa
        row["performance_class"] = _class_from_cgpa(cgpa)
        rows.append(row)
    return pd.DataFrame(rows)


def encode_features(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    encoders: dict[str, LabelEncoder] = {}
    encoded = pd.DataFrame()
    for feature in FEATURES:
        enc = LabelEncoder()
        enc.fit(CATEGORIES[feature])
        encoded[feature] = enc.transform(df[feature])
        encoders[feature] = enc
    return encoded, encoders


def _build_models() -> dict[str, object]:
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
        "XGBoost": XGBClassifier(random_state=42, eval_metric="mlogloss"),
    }


def _evaluate(name: str, model, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    preds = cross_val_predict(model, X, y, cv=skf)
    metrics = {
        "accuracy": accuracy_score(y, preds),
        "f1": f1_score(y, preds, average="weighted", zero_division=0),
    }
    print(
        f"{name:<18} acc={metrics['accuracy']:.3f} f1={metrics['f1']:.3f}"
    )
    return metrics


def train_from_dataframe(df: pd.DataFrame, verbose: bool = True) -> float:
    """Core training routine. Returns validation accuracy."""
    X_df, encoders = encode_features(df)
    target_encoder = LabelEncoder()
    target_encoder.fit(PERFORMANCE_CLASSES)
    y = target_encoder.transform(df["performance_class"])
    X = X_df.to_numpy()

    if HAS_SMOTE and len(np.unique(y)) > 1:
        if verbose:
            print("Applying SMOTE for class balance…")
        try:
            X, y = SMOTE(random_state=42).fit_resample(X, y)
        except Exception as exc:
            if verbose:
                print(f"SMOTE skipped: {exc}")

    if verbose:
        print("\nCross-validated comparison (5-fold):")
    results: dict[str, dict[str, float]] = {}
    for name, model in _build_models().items():
        results[name] = _evaluate(name, model, X, y)

    primary = RandomForestClassifier(n_estimators=150, random_state=42)
    primary.fit(X, y)
    joblib.dump(primary, MODEL_PATH)

    preprocessor = {
        "encoders": encoders,
        "target_encoder": target_encoder,
        "feature_order": FEATURES,
        "classes": list(target_encoder.classes_),
    }
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    importances = sorted(
        (
            {"feature": f, "importance": float(imp)}
            for f, imp in zip(FEATURES, primary.feature_importances_)
        ),
        key=lambda d: d["importance"],
        reverse=True,
    )
    FEATURE_IMPORTANCE_PATH.write_text(json.dumps(importances, indent=2))

    if verbose:
        print("\nFeature importance:")
        for item in importances[:10]:
            print(f"  {item['feature']:<22} {item['importance']:.4f}")
        print(f"\nSaved: {MODEL_PATH.name}, {PREPROCESSOR_PATH.name}")

    return float(results["RandomForest"]["accuracy"])


def train_with_real_data(
    real_rows: list[dict],
    use_synthetic: bool = True,
    synthetic_n: int = 3000,
) -> tuple[float, int]:
    """Blend real survey rows with synthetic data and retrain.

    Returns (accuracy, total_rows_used).
    Each real_row dict must have all feature keys + 'performance_class'.
    """
    frames: list[pd.DataFrame] = []

    if real_rows:
        real_df = pd.DataFrame(real_rows)
        for feature, options in CATEGORIES.items():
            if feature in real_df.columns:
                real_df = real_df[real_df[feature].isin(options)]
        real_df = real_df[[*FEATURES, "performance_class"]].dropna()
        if not real_df.empty:
            frames.append(real_df)

    if use_synthetic:
        synth_df = generate_synthetic_data(synthetic_n)
        frames.append(synth_df[[*FEATURES, "performance_class"]])

    if not frames:
        raise ValueError("No valid training rows provided.")

    df = pd.concat(frames, ignore_index=True)
    print(f"Total training rows: {len(df)}")
    print("Class distribution:\n", df["performance_class"].value_counts())

    accuracy = train_from_dataframe(df)
    return accuracy, len(df)


def main() -> None:
    print("Generating synthetic dataset…")
    n = int(os.environ.get("TRAIN_SAMPLES", "5000"))
    df = generate_synthetic_data(n)
    print(f"Dataset size: {len(df)}")
    print("Class distribution:\n", df["performance_class"].value_counts())
    train_from_dataframe(df)


if __name__ == "__main__":
    main()
