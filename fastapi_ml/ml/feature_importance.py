"""Generate the feature-importance JSON from the trained model.

Run:  python -m ml.feature_importance   (from the fastapi_ml/ directory)
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib

HERE = Path(__file__).resolve().parent
MODEL_PATH = HERE / "model.pkl"
PREPROCESSOR_PATH = HERE / "preprocessor.pkl"
OUTPUT_PATH = HERE / "feature_importance.json"


def compute_feature_importance() -> list[dict[str, float]]:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    features = preprocessor["feature_order"]
    pairs = zip(features, model.feature_importances_)
    return sorted(
        ({"feature": f, "importance": float(imp)} for f, imp in pairs),
        key=lambda d: d["importance"],
        reverse=True,
    )


def main() -> None:
    importances = compute_feature_importance()
    OUTPUT_PATH.write_text(json.dumps(importances, indent=2))
    for item in importances:
        print(f"{item['feature']:<18} {item['importance']:.4f}")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
