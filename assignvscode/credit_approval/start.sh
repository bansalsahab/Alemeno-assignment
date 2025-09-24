#!/bin/sh
set -e

# Wait for DB
python app/manage.py wait_for_db

# Run migrations
python app/manage.py migrate

# Ingest initial data (schedules Celery tasks)
python app/manage.py ingest_initial_data &

# Start Gunicorn
exec gunicorn credit_approval.wsgi:application --chdir app --bind 0.0.0.0:8000
