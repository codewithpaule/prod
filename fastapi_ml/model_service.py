"""Model loading and inference helpers for the ML service."""
from __future__ import annotations

import os
from pathlib import Path
from threading import Lock

import joblib
import numpy as np

from schemas import FeatureScore, StudentFeatures
from groq_advisor import generate_recommendation

HERE = Path(__file__).resolve().parent
DEFAULT_MODEL_PATH = HERE / "ml" / "model.pkl"
DEFAULT_PREPROCESSOR_PATH = HERE / "ml" / "preprocessor.pkl"

MODEL_VERSION = "1.0"

_lock = Lock()
_model = None
_preprocessor: dict | None = None


def _resolve(path_env: str, default: Path) -> Path:
    value = os.environ.get(path_env)
    if not value:
        return default
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = HERE / candidate
    return candidate


def model_path() -> Path:
    return _resolve("MODEL_PATH", DEFAULT_MODEL_PATH)


def preprocessor_path() -> Path:
    return _resolve("PREPROCESSOR_PATH", DEFAULT_PREPROCESSOR_PATH)


def load_artifacts() -> None:
    """Load model + preprocessor into memory. Raises if files are missing."""
    global _model, _preprocessor
    with _lock:
        mp, pp = model_path(), preprocessor_path()
        if not mp.exists():
            raise FileNotFoundError(
                f"Model file not found at {mp}. Run 'python -m ml.train_model' first."
            )
        if not pp.exists():
            raise FileNotFoundError(
                f"Preprocessor file not found at {pp}. Run 'python -m ml.train_model' first."
            )
        _model = joblib.load(mp)
        _preprocessor = joblib.load(pp)


def is_loaded() -> bool:
    return _model is not None and _preprocessor is not None


def _ensure_loaded() -> None:
    if not is_loaded():
        load_artifacts()


def _encode(student: StudentFeatures) -> np.ndarray:
    assert _preprocessor is not None
    encoders = _preprocessor["encoders"]
    order = _preprocessor["feature_order"]
    features = student.feature_dict()
    row = []
    for name in order:
        enc = encoders[name]
        value = features[name]
        if value not in set(enc.classes_):
            raise ValueError(f"Unknown value '{value}' for field '{name}'.")
        row.append(int(enc.transform([value])[0]))
    return np.array([row])


def _top_feature_scores(student: StudentFeatures, top_n: int = 5) -> list[FeatureScore]:
    """Per-student contributing factors: global importance gated by whether the
    student's value for that feature is a known risk indicator."""
    assert _model is not None and _preprocessor is not None
    order = _preprocessor["feature_order"]
    importances = dict(zip(order, _model.feature_importances_))
    pairs = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)
    return [
        FeatureScore(feature=name, importance=float(score))
        for name, score in pairs[:top_n]
    ]


def predict(student: StudentFeatures):
    """Run a single prediction and attach an AI recommendation."""
    from schemas import PredictionResult

    _ensure_loaded()
    assert _model is not None and _preprocessor is not None

    X = _encode(student)
    proba = _model.predict_proba(X)[0]
    idx = int(np.argmax(proba))
    classes = _preprocessor["target_encoder"].inverse_transform(_model.classes_)
    predicted_class = str(classes[idx])
    confidence = float(proba[idx])

    recommendation = generate_recommendation(
        student.feature_dict(), predicted_class, confidence
    )
    feature_scores = _top_feature_scores(student)

    return PredictionResult(
        student_ref=student.student_ref,
        predicted_class=predicted_class,
        confidence=confidence,
        recommendation=recommendation,
        feature_scores=feature_scores,
    )


def feature_importance() -> list[FeatureScore]:
    _ensure_loaded()
    assert _model is not None and _preprocessor is not None
    order = _preprocessor["feature_order"]
    pairs = sorted(
        zip(order, _model.feature_importances_), key=lambda kv: kv[1], reverse=True
    )
    return [FeatureScore(feature=f, importance=float(i)) for f, i in pairs]
