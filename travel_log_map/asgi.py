"""
ASGI config for travel_log_map project.

It exposes the ASGI callable as a module-level variable named ``application``.
This is the entry point for ASGI-compatible web servers to serve the project.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_log_map.settings')

application = get_asgi_application()
