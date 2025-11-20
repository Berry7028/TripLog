#!/usr/bin/env python
"""
Django's command-line utility for administrative tasks.

This module acts as the entry point for running Django management commands,
such as starting the development server, running migrations, and creating
superusers.
"""
import os
import sys


def main():
    """
    Run administrative tasks.

    Sets the default Django settings module to 'travel_log_map.settings'
    and executes the command line arguments using Django's management utility.

    Raises:
        ImportError: If Django cannot be imported, likely due to a missing
            installation or an unactivated virtual environment.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travel_log_map.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
