#!/usr/bin/env bash
# Можно ставить и в Build Command, и в Start Command: ./start.sh
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --noinput

# На этапе сборки PORT не задан — сервер не запускаем
if [ -z "${PORT:-}" ]; then
  exit 0
fi

python manage.py migrate --noinput
python manage.py ensure_initial_data
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}"
