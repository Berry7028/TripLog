#!/bin/bash
set -e

echo "Starting post-deployment setup..."

# Check if superuser environment variables are set
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating Django superuser from environment variables..."
    
    # Create superuser using environment variables
    python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()

import os
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

# Check if user already exists
if User.objects.filter(username=username).exists():
    print(f"Superuser '{username}' already exists")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Superuser '{username}' created successfully")
EOF
    
    echo "Superuser setup completed"
else
    echo "Warning: Superuser environment variables not set. Skipping superuser creation."
    echo "To create a superuser, set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, and DJANGO_SUPERUSER_PASSWORD"
fi

echo "Post-deployment setup finished"
