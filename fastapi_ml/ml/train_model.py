"""Train and compare models for AcadPredict AI.

Generates a realistic synthetic dataset of Nigerian university students (no real
student data is used), engineers a CGPA-derived ``performance_class`` target,
then trains and compares four classifiers with stratified cross-validation. The
Random Forest (primary model) is persisted to ``model.pkl`` and the fitted
label encoders to ``preprocessor.pkl``.

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
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

try:
    from imblearn.over_sampling import SMOTE

    HAS_SMOTE = True
except Exception:  # pragma: no cover - optional dependency at runtime
    HAS_SMOTE = False

from ml.categories import CATEGORIES, PERFORMANCE_CLASSES

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "model.pkl"
PREPROCESSOR_PATH = HERE / "preprocessor.pkl"
FEATURE_IMPORTANCE_PATH = HERE / "feature_importance.json"

FEATURES = list(CATEGORIES.keys())
RNG = np.random.default_rng(42)

# Per-option contribution to a latent "academic strength" score. Higher values
# push a student towards the High class, lower/negative towards At-Risk.
SCORE_WEIGHTS: dict[str, dict[str, float]] = {
    "study_hours": {"<1 hour": -2.0, "1-2 hours": -0.5, "3-4 hours": 1.5, "5+ hours": 2.5},
    "attendance": {"<50%": -2.5, "50-70%": -0.5, "71-90%": 1.5, ">90%": 2.5},
    "courses_failed": {"0": 2.5, "1-2": 0.5, "3-4": -1.5, "5+": -3.0},
    "sleep_hours": {"<4 hours": -1.5, "4-6 hours": 0.5, "7-8 hours": 1.5, ">8 hours": 0.0},
    "financial_stress": {"None": 1.0, "Low": 0.5, "Moderate": -0.5, "High": -1.5},
    "motivation": {"Low": -2.0, "Moderate": 0.5, "High": 2.0},
    "stress_level": {"Low": 1.0, "Moderate": 0.3, "High": -1.0, "Severe": -2.0},
    "self_rated_perf": {"Poor": -2.0, "Average": -0.2, "Good": 1.5, "Excellent": 2.5},
    "mother_education": {"None": -0.8, "Primary": -0.3, "Secondary": 0.3, "Tertiary": 0.8, "Postgraduate": 1.2},
    "father_education": {"None": -0.8, "Primary": -0.3, "Secondary": 0.3, "Tertiary": 0.8, "Postgraduate": 1.2},
    "family_income": {"Low": -0.8, "Lower-Middle": -0.3, "Middle": 0.2, "Upper-Middle": 0.6, "High": 1.0},
    "part_time_work": {"No": 0.4, "Yes - occasionally": 0.0, "Yes - regularly": -0.8},
}


def _cgpa_from_score(score: float) -> float:
    """Map a latent strength score to a plausible CGPA in [0, 5]."""
    base = 2.7 + 0.18 * score
    noise = RNG.normal(0.0, 0.45)
    return float(np.clip(base + noise, 0.0, 5.0))


def _class_from_cgpa(cgpa: float) -> str:
    if cgpa >= 3.5:
        return "High"
    if cgpa >= 2.5:
        return "Average"
    return "At-Risk"


def generate_synthetic_data(n: int = 4000) -> pd.DataFrame:
    """Generate a synthetic, learnable dataset of student survey rows."""
    rows: list[dict[str, str | float]] = []
    for _ in range(n):
        row: dict[str, str | float] = {
            feature: str(RNG.choice(options)) for feature, options in CATEGORIES.items()
        }
        score = sum(
            SCORE_WEIGHTS.get(feature, {}).get(str(row[feature]), 0.0) for feature in FEATURES
        )
        cgpa = _cgpa_from_score(score)
        row["cgpa"] = cgpa
        row["performance_class"] = _class_from_cgpa(cgpa)
        rows.append(row)
    return pd.DataFrame(rows)


def clean_contradictions(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows where CGPA and self-rated performance badly contradict."""
    contradiction = (
        (df["performance_class"] == "At-Risk") & (df["self_rated_perf"] == "Excellent")
    ) | ((df["performance_class"] == "High") & (df["self_rated_perf"] == "Poor"))
    return df.loc[~contradiction].reset_index(drop=True)


def encode_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
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
        "RandomForest": RandomForestClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(random_state=42, eval_metric="mlogloss"),
    }


def _evaluate(name: str, model, X: np.ndarray, y: np.ndarray) -> dict[str, float]:
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    preds = cross_val_predict(model, X, y, cv=skf)
    proba = cross_val_predict(model, X, y, cv=skf, method="predict_proba")
    metrics = {
        "accuracy": accuracy_score(y, preds),
        "precision": precision_score(y, preds, average="weighted", zero_division=0),
        "recall": recall_score(y, preds, average="weighted", zero_division=0),
        "f1": f1_score(y, preds, average="weighted", zero_division=0),
        "roc_auc": roc_auc_score(y, proba, multi_class="ovr", average="weighted"),
    }
    print(
        f"{name:<18} "
        f"acc={metrics['accuracy']:.3f} "
        f"prec={metrics['precision']:.3f} "
        f"rec={metrics['recall']:.3f} "
        f"f1={metrics['f1']:.3f} "
        f"roc_auc={metrics['roc_auc']:.3f}"
    )
    return metrics


def main() -> None:
    print("Generating synthetic dataset...")
    df = generate_synthetic_data(int(os.environ.get("TRAIN_SAMPLES", "4000")))
    df = clean_contradictions(df)
    print(f"Dataset size after cleaning: {len(df)} rows")
    print("Class distribution:\n", df["performance_class"].value_counts())

    X_df, encoders = encode_features(df)
    target_encoder = LabelEncoder()
    target_encoder.fit(PERFORMANCE_CLASSES)
    y = target_encoder.transform(df["performance_class"])
    X = X_df.to_numpy()

    if HAS_SMOTE:
        print("Applying SMOTE for class balance...")
        X, y = SMOTE(random_state=42).fit_resample(X, y)
    else:
        print("imbalanced-learn not available; skipping SMOTE.")

    print("\nCross-validated model comparison (5-fold StratifiedKFold):")
    results: dict[str, dict[str, float]] = {}
    for name, model in _build_models().items():
        results[name] = _evaluate(name, model, X, y)

    best_name = max(results, key=lambda n: results[n]["f1"])
    print(f"\nBest model by weighted F1: {best_name}")
    print("Persisting RandomForest as the primary production model (model.pkl).")

    primary = RandomForestClassifier(n_estimators=100, random_state=42)
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
        ({"feature": f, "importance": float(imp)} for f, imp in zip(FEATURES, primary.feature_importances_)),
        key=lambda d: d["importance"],
        reverse=True,
    )
    FEATURE_IMPORTANCE_PATH.write_text(json.dumps(importances, indent=2))

    print("\nFeature importance (sorted descending):")
    for item in importances:
        print(f"  {item['feature']:<18} {item['importance']:.4f}")

    print(f"\nSaved: {MODEL_PATH.name}, {PREPROCESSOR_PATH.name}, {FEATURE_IMPORTANCE_PATH.name}")


if __name__ == "__main__":
    main()
