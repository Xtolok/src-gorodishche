#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py populate_site
python manage.py import_about_volganet
python manage.py import_legal_volganet
python manage.py import_current_volganet
python manage.py import_nok_volganet
python manage.py collectstatic --noinput
