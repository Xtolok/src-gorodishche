#!/usr/bin/env bash
# Render → Start Command
set -o errexit

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-10000}"
