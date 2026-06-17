# AcadPredict AI

A student academic performance prediction system for Nigerian universities,
built with machine learning and **Groq AI**.

> AI recommendations are powered by **Groq** (the original spec called for
> Anthropic Claude; this implementation uses Groq instead).

## Architecture

| Layer            | Tech                                            | Folder        |
| ---------------- | ----------------------------------------------- | ------------- |
| Web layer        | Django 4.2 + Python 3.11                        | `django_app/` |
| ML/AI layer      | FastAPI + Uvicorn (async)                       | `fastapi_ml/` |
| Database         | PostgreSQL via Supabase                         | —             |
| Frontend         | HTML5 + CSS3 + Vanilla JS + Chart.js (CDN)      | —             |
| ML libraries     | scikit-learn, XGBoost, pandas, numpy, joblib    | —             |
| AI integration   | Groq (`llama-3.3-70b-versatile`)                | `fastapi_ml/groq_advisor.py` |

The Django app handles auth, the UI, and persistence; it calls the FastAPI
service for predictions and AI recommendations.

## Features

- Login-protected dashboard with three Chart.js charts (distribution doughnut,
  feature-importance bar, 30-day trend line)
- Single-student prediction form with AI advisor recommendation
- Bulk CSV upload (with sample download + per-row validation)
- Paginated students table with risk filtering and CSV export
- Random Forest classifier (primary) compared against Logistic Regression,
  Decision Tree and XGBoost during training

## Quick start

See [DEPLOYMENT.md](DEPLOYMENT.md) for full local + Railway/Supabase instructions.

```bash
# ML service
cd fastapi_ml && pip install -r requirements.txt
python -m ml.train_model          # trains from ../responses.csv
uvicorn main:app --port 8001

# Web service
cd django_app && pip install -r requirements.txt
export FASTAPI_URL=http://127.0.0.1:8001 DEBUG=True
python manage.py migrate && python manage.py createsuperuser
python manage.py runserver 8000
```

## Environment variables

**Django (`django_app/.env`)** — `SECRET_KEY`, `DATABASE_URL`, `FASTAPI_URL`,
`DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`

**FastAPI (`fastapi_ml/.env`)** — `GROQ_API_KEY`, `GROQ_MODEL` (optional),
`MODEL_PATH`, `PREPROCESSOR_PATH`

See the `.env.example` file in each service folder.
