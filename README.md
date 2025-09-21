# TripLog

A Django-based travel log mapping application deployed on Render.com. Share and discover travel spots with interactive maps.

## Features

- Interactive map for exploring travel spots
- User authentication and travel log sharing
- Automatic superuser creation for production deployments
- Post-deployment setup automation

## Deployment Setup

### Environment Variables

For production deployment on Render.com, set the following environment variables:

#### Required for Django
- `SECRET_KEY`: Django secret key for security
- `DEBUG`: Set to `false` for production
- `DATABASE_URL`: PostgreSQL database URL (automatically provided by Render)

#### Superuser Auto-Creation
To automatically create an admin superuser during deployment, set these environment variables:

- `DJANGO_SUPERUSER_USERNAME`: Admin username (e.g., `admin`)
- `DJANGO_SUPERUSER_EMAIL`: Admin email address
- `DJANGO_SUPERUSER_PASSWORD`: Admin password (e.g., `admin123`)

### Automatic Deployment Process

1. **Database Setup**: `python manage.py migrate`
2. **Static Files**: `python manage.py collectstatic --no-input`
3. **Post-Deployment**: Executes `post_deploy.sh` for superuser creation
4. **Server Start**: Starts Gunicorn server

### Files Structure

```
├── post_deploy.sh          # Post-deployment script for superuser creation
├── start.sh                # Main deployment startup script
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
├── travel_log_map/        # Django project settings
└── spots/                 # Django app for travel spots
```

### Manual Deployment

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set environment variables
4. Run migrations: `python manage.py migrate`
5. Create superuser: `python manage.py createsuperuser`
6. Start development server: `python manage.py runserver`

## Admin Access

After deployment, access the admin panel at:
- **URL**: `https://your-domain.com/admin/`
- **Username**: Value of `DJANGO_SUPERUSER_USERNAME` environment variable
- **Password**: Value of `DJANGO_SUPERUSER_PASSWORD` environment variable

## Development

### Local Setup

```bash
git clone https://github.com/Berry7028/TripLog.git
cd TripLog
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Scripts

- `start.sh`: Production startup script with post-deployment setup
- `post_deploy.sh`: Automated superuser creation from environment variables
- Development scripts available in `scripts/` directory

## Technology Stack

- **Backend**: Django 5.2+
- **Database**: PostgreSQL (production), SQLite (development)
- **Deployment**: Render.com
- **Web Server**: Gunicorn
- **Static Files**: WhiteNoise

## Contributing

See `AGENTS.md` and `README_scripts.md` for development guidelines and available scripts.

## License

This project is private and not licensed for public use.
