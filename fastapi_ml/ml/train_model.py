"""Train and compare models for AcadPredict AI.

Trains on real survey responses from responses.csv. Synthetic data blending
is optional and disabled by default.

Run:  python -m ml.train_model   (from the fastapi_ml/ directory)
      python -m ml.train_from_real_data   (explicit CSV trainer)
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
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
BIAS_REPORT_PATH = HERE / "bias_report.json"

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


def encode_features(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, LabelEncoder]]:
    encoders: dict[str, LabelEncoder] = {}
    encoded = pd.DataFrame()
    for feature in FEATURES:
        enc = LabelEncoder()
        enc.fit(CATEGORIES[feature])
        encoded[feature] = enc.transform(df[feature])
        encoders[feature] = enc
    return encoded, encoders


def _cv_folds(y: np.ndarray, max_splits: int = 5) -> int:
    """Pick a stratified fold count that works for small / imbalanced datasets."""
    min_class = int(np.bincount(y)[np.bincount(y) > 0].min())
    return max(2, min(max_splits, min_class, len(y)))


def _build_models() -> dict[str, object]:
    return {
        "LogisticRegression": LogisticRegression(max_iter=1000),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=150, random_state=42),
        "XGBoost": XGBClassifier(random_state=42, eval_metric="mlogloss"),
    }


def _evaluate(name: str, model, X: np.ndarray, y: np.ndarray) -> dict[str, float] | None:
    n_splits = _cv_folds(y)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    try:
        preds = cross_val_predict(model, X, y, cv=skf)
    except ValueError as exc:
        print(f"{name:<18} skipped ({exc})")
        return None
    metrics = {
        "accuracy": accuracy_score(y, preds),
        "f1": f1_score(y, preds, average="weighted", zero_division=0),
    }
    print(f"{name:<18} acc={metrics['accuracy']:.3f} f1={metrics['f1']:.3f} ({n_splits}-fold)")
    return metrics


def check_bias(df: pd.DataFrame, y_pred: np.ndarray, target_encoder: LabelEncoder) -> dict:
    """Check accuracy parity across gender and level subgroups.

    Returns a dict describing any subgroups with accuracy more than 10pp
    below the overall — these are potential bias flags.
    """
    y_true_labels = df["performance_class"].values
    y_pred_labels = target_encoder.inverse_transform(y_pred)

    overall_acc = float(np.mean(y_true_labels == y_pred_labels))
    threshold = overall_acc - 0.10  # flag if more than 10pp below overall

    bias_flags: list[dict] = []
    report: dict = {"overall_accuracy": round(overall_acc, 4), "subgroup_checks": [], "flags": []}

    for group_col in ("gender", "level"):
        if group_col not in df.columns:
            continue
        for group_val in df[group_col].unique():
            mask = df[group_col] == group_val
            if mask.sum() < 5:
                continue
            grp_acc = float(np.mean(y_true_labels[mask] == y_pred_labels[mask]))
            entry = {
                "group": group_col,
                "value": str(group_val),
                "n": int(mask.sum()),
                "accuracy": round(grp_acc, 4),
            }
            report["subgroup_checks"].append(entry)
            if grp_acc < threshold:
                flag = f"WARNING: {group_col}={group_val} accuracy={grp_acc:.1%} is >10pp below overall ({overall_acc:.1%})"
                report["flags"].append(flag)
                print(f"  BIAS FLAG — {flag}")

    if not report["flags"]:
        print("  No significant bias detected across gender/level subgroups.")

    return report


def train_from_dataframe(df: pd.DataFrame, verbose: bool = True) -> tuple[float, dict]:
    """Core training routine. Returns (validation_accuracy, bias_report)."""
    X_df, encoders = encode_features(df)
    target_encoder = LabelEncoder()
    target_encoder.fit(PERFORMANCE_CLASSES)
    y = target_encoder.transform(df["performance_class"])
    X = X_df.to_numpy()

    if HAS_SMOTE and len(np.unique(y)) > 1:
        min_class = int(np.bincount(y)[np.bincount(y) > 0].min())
        if min_class >= 6:
            if verbose:
                print("Applying SMOTE to balance classes …")
            try:
                X_res, y_res = SMOTE(random_state=42).fit_resample(X, y)
                print(f"  After SMOTE: {len(y_res)} rows (was {len(y)})")
                X, y = X_res, y_res
            except Exception as exc:
                if verbose:
                    print(f"  SMOTE skipped: {exc}")
        elif verbose:
            print(f"SMOTE skipped: smallest class has only {min_class} sample(s).")

    n_splits = _cv_folds(y)
    if verbose:
        print(f"\nCross-validated model comparison ({n_splits}-fold):")
    results: dict[str, dict[str, float]] = {}
    for name, model in _build_models().items():
        metrics = _evaluate(name, model, X, y)
        if metrics is not None:
            results[name] = metrics

    primary = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")

    if verbose:
        print("\nBias / fairness check (cross-validated, original distribution):")
    X_orig_df, _ = encode_features(df)
    y_orig = target_encoder.transform(df["performance_class"])
    skf_bias = StratifiedKFold(n_splits=_cv_folds(y_orig), shuffle=True, random_state=99)
    y_pred_cv = cross_val_predict(primary, X_orig_df.to_numpy(), y_orig, cv=skf_bias)
    bias_report = check_bias(df, y_pred_cv, target_encoder)

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
    BIAS_REPORT_PATH.write_text(json.dumps(bias_report, indent=2))

    if verbose:
        print("\nTop feature importances:")
        for item in importances[:10]:
            print(f"  {item['feature']:<22} {item['importance']:.4f}")
        print(f"\nSaved model, preprocessor, feature_importance, bias_report.")

    best_acc = results.get("RandomForest", {}).get("accuracy")
    if best_acc is None and results:
        best_acc = next(iter(results.values()))["accuracy"]
    return float(best_acc or 0.0), bias_report


def train_with_real_data(
    real_rows: list[dict],
    use_synthetic: bool = False,
    synthetic_n: int = 3000,
) -> tuple[float, int, dict]:
    """Train on real survey rows, optionally blended with synthetic data.
    Returns (accuracy, total_rows_used, bias_report).
    """
    frames: list[pd.DataFrame] = []

    if real_rows:
        real_df = pd.DataFrame(real_rows)
        for feature, options in CATEGORIES.items():
            if feature in real_df.columns:
                real_df = real_df[real_df[feature].isin(options)]
        cols = [f for f in FEATURES if f in real_df.columns] + ["performance_class"]
        real_df = real_df[cols].dropna()

        # Fill any missing features with the most common value (median imputation)
        for feat in FEATURES:
            if feat not in real_df.columns:
                real_df[feat] = CATEGORIES[feat][0]

        if not real_df.empty:
            frames.append(real_df[[*FEATURES, "performance_class"]])
            print(f"Real data: {len(real_df)} rows")
            print("Real class distribution:\n", real_df["performance_class"].value_counts().to_string())

    if use_synthetic:
        synth_df = generate_synthetic_data(synthetic_n)
        frames.append(synth_df[[*FEATURES, "performance_class"]])
        print(f"Synthetic data: {synthetic_n} rows")

    if not frames:
        raise ValueError("No valid training rows provided.")

    df = pd.concat(frames, ignore_index=True)
    print(f"\nTotal training rows: {len(df)}")
    print("Overall class distribution:\n", df["performance_class"].value_counts().to_string())

    accuracy, bias_report = train_from_dataframe(df)
    return accuracy, len(df), bias_report


def main() -> None:
    from ml.train_from_real_data import DEFAULT_CSV, main as train_real

    if DEFAULT_CSV.exists():
        train_real(DEFAULT_CSV)
        return

    raise FileNotFoundError(
        f"No training data found at {DEFAULT_CSV}. "
        "Place your Google Form export as responses.csv at the repo root."
    )


if __name__ == "__main__":
    main()
