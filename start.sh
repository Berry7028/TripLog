#!/bin/bash
set -e

# Production start script for Render.com

# Set production environment
export DEBUG=False
export DJANGO_SETTINGS_MODULE=travel_log_map.settings

# Run database migrations
python manage.py collectstatic --no-input
python manage.py migrate

# Verify static files are collected correctly
echo "Verifying static files collection..."
python manage.py findstatic spots/css/style.css -v 2

# Run post-deployment setup (including superuser creation)
if [ -f "./post_deploy.sh" ]; then
    echo "Running post-deployment setup..."
    chmod +x ./post_deploy.sh
    ./post_deploy.sh
else
    echo "Warning: post_deploy.sh not found"
fi

# Start the Django application with Gunicorn
exec gunicorn travel_log_map.wsgi:application --bind 0.0.0.0:$PORT
