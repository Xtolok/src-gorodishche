#!/usr/bin/env bash
# Render → Start Command (free tier: bootstrap здесь, т.к. Pre-Deploy только на платном)
set -o errexit

BOOTSTRAP_MARKER=/tmp/.site_bootstrapped

if [ ! -f "$BOOTSTRAP_MARKER" ]; then
  echo "=== Первый запуск инстанса: инициализация БД и данных ==="
  # RENDER=true выставляется Render автоматически
  bash "$(dirname "$0")/predeploy.sh"
  touch "$BOOTSTRAP_MARKER"
  echo "=== Инициализация завершена ==="
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
