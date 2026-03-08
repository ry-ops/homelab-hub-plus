#!/bin/sh
set -e

echo "Starting application (git-steer storage)..."
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --timeout 120 wsgi:app
