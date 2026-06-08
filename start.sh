#!/usr/bin/env bash
set -o errexit

python manage.py migrate --noinput
python manage.py ensure_initial_data
exec gunicorn config.wsgi:application
