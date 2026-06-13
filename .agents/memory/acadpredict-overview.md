---
name: AcadPredict project overview
description: Architecture, ports, key files, and conventions for the AcadPredict AI project.
---

## Architecture
- Django on port 5000 (gunicorn), FastAPI ML service on port 8001 (uvicorn, localhost only)
- Django calls FastAPI via HTTP; FASTAPI_URL=http://127.0.0.1:8001
- Startup: `bash start.sh` — FastAPI first, then Django migrations + gunicorn

## Key files
- `start.sh` — startup script
- `fastapi_ml/ml/categories.py` — canonical 26 features + CGPA class definitions (source of truth)
- `django_app/core/choices.py` — Django mirror of categories (must stay in sync)
- `fastapi_ml/ml/train_model.py` — training logic, bias checking, SMOTE
- `fastapi_ml/ml/train_from_real_data.py` — direct CSV trainer for the specific Google Form
- `django_app/core/google_form_mapping.py` — column + value mapping for Google Form exports
- `django_app/core/models.py` — Student, Prediction, AdvisorNote, TrainingBatch

## Model
- RandomForest 200 trees, class_weight=balanced, 26 features, 5 CGPA band classes
- CGPA bands: First Class (4.5-5.0), 2nd Upper (3.5-4.4), 2nd Lower (2.5-3.4), Third (1.5-2.4), Below (<1.5)
- Artifacts: `fastapi_ml/ml/model.pkl`, `preprocessor.pkl`, `feature_importance.json`, `bias_report.json`
- Current accuracy: ~78.8% with 60 real rows + 4000 synthetic

## Important conventions
- ALLOWED_HOSTS = ["*"] in Django settings for Replit proxy
- All 26 survey Q headers and values use unicode en-dash (–) in Google Form exports; mapping in google_form_mapping.py handles this
- "600 Level" students mapped to "500" (proxy, not a real category)
- `train_with_real_data()` returns (accuracy, total_rows, bias_report) — 3 values
