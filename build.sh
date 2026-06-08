#!/usr/bin/env bash
# То же самое, что start.sh (для ясности в настройках Render)
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput
