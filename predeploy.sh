#!/usr/bin/env bash
# Инициализация сайта: вызывается из start.sh (free tier) или Pre-Deploy (платный)
set -o errexit
echo "=== Миграции ==="
python manage.py migrate --noinput

echo "=== Базовые данные (если БД пустая) ==="
python manage.py ensure_initial_data

echo "=== Статический контент сайта ==="
python manage.py populate_site

echo "=== Импорт с volganet.ru ==="
python manage.py import_about_volganet
python manage.py import_legal_volganet
python manage.py import_current_volganet
python manage.py import_nok_volganet

echo "=== Администратор ==="
python manage.py ensure_admin
