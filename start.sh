#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py ensure_initial_data
python manage.py ensure_admin

if [ -z "${PORT:-}" ]; then
  exit 0
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}"
