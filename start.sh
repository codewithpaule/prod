#!/bin/bash
set -e

cd "$(dirname "$0")"

# Start FastAPI ML service on port 8001 (background)
cd fastapi_ml
uvicorn main:app --host 127.0.0.1 --port 8001 &
FASTAPI_PID=$!
cd ..

# Give FastAPI a moment to start
sleep 2

# Run Django migrations and collect static files
cd django_app
python manage.py migrate
python manage.py collectstatic --noinput

# Start Django on port 5000
FASTAPI_URL=http://127.0.0.1:8001 \
DEBUG=True \
gunicorn acadpredict_web.wsgi:application \
  --bind 0.0.0.0:5000 \
  --workers 2 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile - &
DJANGO_PID=$!

cd ..

# Wait for either process to exit
wait $FASTAPI_PID $DJANGO_PID
