"""
Configuration for the Spots Django application.
"""

from django.apps import AppConfig


class SpotsConfig(AppConfig):
    """
    AppConfig class for the 'spots' application.

    Defines the default auto field and the application name.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'spots'
