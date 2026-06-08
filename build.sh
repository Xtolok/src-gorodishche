#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py loaddata initial_data
python manage.py collectstatic --noinput
