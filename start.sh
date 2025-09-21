#!/bin/bash
set -e

# Production start script for Render.com

# Run database migrations
python manage.py collectstatic --no-input
python manage.py migrate

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
