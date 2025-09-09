# Repository Guidelines

## Project Structure & Module Organization
- Django project root: `travel_log_map/` (settings, URLs, WSGI).
- Main app: `spots/` (models, views, templates, static, migrations).
- Database: `db.sqlite3` (local development only).
- Virtual env (optional): `venv/`.
- Static assets: `spots/static/`; templates: `spots/templates/`.

## Build, Test, and Development Commands
- Create env and install: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`.
- Run server (dev): `python manage.py runserver`.
- DB migrations: `python manage.py makemigrations && python manage.py migrate`.
- Superuser: `python manage.py createsuperuser`.
- Tests: `python manage.py test`.

## Coding Style & Naming Conventions
- Python: PEP 8, 4‑space indent, UTF‑8.
- Names: modules/functions `snake_case`, classes `CapWords`, template files `lowercase_with_underscores.html`.
- Django conventions: views in `views.py` or `views/*.py`, URLs in `spots/urls.py`; keep URL names stable (e.g., `add_spot`, `spot_detail`).
- Templates: keep under `spots/templates/` with folders per feature when they grow (e.g., `spots/templates/spots/detail.html`).
- Static: place CSS/JS/images under `spots/static/spots/` and reference via `{% static %}`.

## Testing Guidelines
- Framework: Django `unittest`.
- Location: `spots/tests/` with files like `test_views.py`, `test_models.py`.
- Naming: test classes `Test...`, methods `test_...`.
- Use factories/fixtures sparingly; prefer model creation helpers.
- Aim for coverage of model methods, key views, and API endpoints under `spots/urls.py`.

## Commit & Pull Request Guidelines
- Commits: concise, imperative mood (e.g., "Add spot detail view"). Group related changes.
- Reference issues in commits/PRs (e.g., `Fixes #12`).
- PRs: include purpose, scope, screenshots for UI changes, migration notes, and manual test steps. Keep PRs focused and under ~300 lines when possible.

## Security & Configuration Tips
- Do not commit secrets. `SECRET_KEY`, tokens, and prod settings must live in environment variables.
- Dev only: `DEBUG=True`, `ALLOWED_HOSTS=['*']`. For prod, set strict `ALLOWED_HOSTS`, `DEBUG=False`, and review `CSRF_TRUSTED_ORIGINS` in `travel_log_map/settings.py`.
- Run `migrate` after pulling schema changes; include generated migrations in PRs.

## Architecture Overview
- Classic Django MVC: URL routes (`travel_log_map/urls.py`, `spots/urls.py`) → views in `spots/views.py` → templates/static in `spots/`.
- SQLite for local dev; swap `DATABASES` for production.
