# Repository Guidelines

## Project Structure & Module Organization
`travel_log_map/` holds project settings, URL routers, and WSGI entrypoints. Feature code sits in `spots/` (models, views, templates, static, migrations). Templates belong in `spots/templates/spots/`; static files go in `spots/static/spots/`. Tests live in `spots/tests/` next to the modules they cover. Scripts and dev helpers stay in `scripts/`. Leave `db.sqlite3` and `media/` out of commits; they are dev artifacts. Use `venv/` for isolated Python deps.

## Build, Test, and Development Commands
`python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` sets up dependencies. `python manage.py runserver` starts the local server on `http://127.0.0.1:8000`. Run `python manage.py makemigrations && python manage.py migrate` whenever models change. Use `python manage.py createsuperuser` to seed admin credentials for manual QA. Execute `python manage.py test` (or `python manage.py test spots`) before pushing.

## Coding Style & Naming Conventions
Write Python in PEP 8 style with 4-space indents and UTF-8 encoding. Favor `snake_case` for modules, functions, and variables; classes use `CapWords`; templates follow `lowercase_with_underscores.html`. Keep view logic in `spots/views.py` or feature-specific modules under `spots/views/`, and register routes in `spots/urls.py` with stable names (`add_spot`, `spot_detail`). Load assets via `{% static 'spots/<path>' %}`.

## Testing Guidelines
Tests use Django’s unittest runner. Organize cases in `spots/tests/` mirroring the feature layout, naming classes `Test...` and methods `test_...`. Create objects inline or with helper builders instead of heavyweight fixtures. Assert on status codes, context data, and model side effects. Aim to keep `python manage.py test` clean before requesting review.

## Commit & Pull Request Guidelines
Commits stay small, imperative, and focused (e.g., `Add spot detail view`). Reference issues with `Fixes #id` when applicable. Pull requests should explain the change, list manual test steps, and attach UI screenshots for visual updates. Flag migrations and note any config changes. Target PR payloads under roughly 300 changed lines so reviewers can focus.

## Security & Configuration Tips
Never hardcode secrets; pull them from environment variables or ignored `.env` files. `DEBUG=True` and permissive `ALLOWED_HOSTS` are acceptable locally, but production must set `DEBUG=False`, tighten hosts, and review `CSRF_TRUSTED_ORIGINS`. Revisit `travel_log_map/settings.py` whenever adding storage backends, maps APIs, or outbound integrations.

## Architecture Overview
Requests flow through `travel_log_map/urls.py` into `spots/urls.py`, invoke view functions or class-based views in `spots/views.py`, and render templates under `spots/templates/`. Persistent data sits in SQLite for dev; adjust `DATABASES` before deploying elsewhere. Static assets serve from `spots/static/`, while uploads land in `media/`.
