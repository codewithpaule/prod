# Deployment Guide — AcadPredict AI

AcadPredict AI runs as **two services** on Railway plus a **Supabase** PostgreSQL
database:

1. `django_app/` — the web layer (UI, auth, persistence)
2. `fastapi_ml/` — the ML/AI layer (model inference + Groq recommendations)

The AI advisor uses **Groq** (not Anthropic Claude). You will need a Groq API key
from <https://console.groq.com>.

---

## 1. Create the Supabase database

1. Create a project at <https://supabase.com>.
2. In **Project Settings → Database**, copy the connection string. It looks like:
   ```
   postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres
   ```
3. Keep this as `DATABASE_URL` for the Django service.

## 2. Deploy the FastAPI ML service (Service 1)

1. Create a new Railway service from this repo and set the **root directory** to
   `fastapi_ml`.
2. Railway installs `requirements.txt` and runs the `Procfile`:
   ```
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
3. Set environment variables:
   | Variable            | Example                          |
   | ------------------- | -------------------------------- |
   | `GROQ_API_KEY`      | `gsk_...`                        |
   | `GROQ_MODEL`        | `llama-3.3-70b-versatile` (opt.) |
   | `MODEL_PATH`        | `ml/model.pkl`                   |
   | `PREPROCESSOR_PATH` | `ml/preprocessor.pkl`            |
4. The trained `model.pkl` / `preprocessor.pkl` are committed to the repo. To
   retrain from your survey data, place `responses.csv` at the repo root and run
   `python -m ml.train_model` from `fastapi_ml/`.
5. After deploy, note the public URL, e.g. `https://acadpredict-ml.up.railway.app`.

## 3. Deploy the Django web service (Service 2)

1. Create a second Railway service from the same repo with **root directory**
   `django_app`.
2. The `Procfile` runs migrations on release and serves via gunicorn:
   ```
   web: gunicorn acadpredict_web.wsgi --bind 0.0.0.0:$PORT
   release: python manage.py migrate --noinput
   ```
3. Set environment variables:
   | Variable               | Example                                             |
   | ---------------------- | --------------------------------------------------- |
   | `SECRET_KEY`           | a long random string                                |
   | `DATABASE_URL`         | the Supabase connection string from step 1          |
   | `FASTAPI_URL`          | the Railway URL from step 2                          |
   | `DEBUG`                | `False`                                             |
   | `ALLOWED_HOSTS`        | `your-django-domain.railway.app,yourdomain.com.ng`  |
   | `CSRF_TRUSTED_ORIGINS` | `https://your-django-domain.railway.app`            |

## 4. Wire the two services together

Set `FASTAPI_URL` in the Django service to the FastAPI service's public URL
(step 2). The Django app calls `/predict`, `/predict-bulk`, and
`/feature-importance` on that host.

## 5. Run migrations

Migrations run automatically via the `release` command. To run manually, open the
Railway shell for the Django service:
```
python manage.py migrate
```

## 6. Create a superuser

In the Railway shell for the Django service:
```
python manage.py createsuperuser
```
Use these credentials to sign in at `/login`.

## 7. Custom domain

Point your custom `.com.ng` domain at the **Django** service in Railway's domain
settings, and add it to both `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.

---

## Local development

```bash
# 1. FastAPI ML service
cd fastapi_ml
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m ml.train_model           # trains from ../responses.csv
export GROQ_API_KEY=gsk_...         # optional; falls back to rule-based advice
uvicorn main:app --reload --port 8001

# 2. Django web service (new terminal)
cd django_app
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FASTAPI_URL=http://127.0.0.1:8001
export DEBUG=True
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 8000
```

Then open <http://127.0.0.1:8000/login>.

> If `GROQ_API_KEY` is not set, the ML service returns a deterministic, rule-based
> recommendation so the full flow still works without external calls.
