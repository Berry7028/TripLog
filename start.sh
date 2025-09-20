#!/bin/bash
set -e

# Production start script for Render.com
# Run database migrations
python manage.py collectstatic --no-input
python manage.py migrate

# Start the Django application with Gunicorn
exec gunicorn travel_log_map.wsgi:application --bind 0.0.0.0:$PORT
