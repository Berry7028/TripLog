# TripLog

A Django-based travel log mapping application deployed on Render.com. Share and discover travel spots through an interactive map.

## Purpose

TripLog allows users to document their travel experiences by pinning spots on a map, adding descriptions, images, and ratings. It provides a platform for users to share their journeys and discover new destinations recommended by others.

## Features

- **Interactive Map**: Explore travel spots visually on a map.
- **User Authentication**: Secure signup, login, and profile management.
- **Spot Management**: Create, edit, and delete travel spots with images and tags.
- **Reviews**: Rate and review spots shared by other users.
- **Favorites**: Save interesting spots to your personal list.
- **Admin Dashboard**: Custom dashboard for staff to manage content and users.
- **Automated Deployment**: Scripts for automatic setup and superuser creation on Render.com.

## Setup for New Developers

### Prerequisites

- Python 3.9+
- pip (Python package installer)
- Git

### Local Development Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/Berry7028/TripLog.git
    cd TripLog
    ```

2.  **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**

    ```bash
    python manage.py migrate
    ```

5.  **Create a superuser (admin):**

    ```bash
    python manage.py createsuperuser
    ```

6.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

    Access the application at `http://127.0.0.1:8000/`.

### Usage

-   **Home**: View the list of recent spots.
-   **Map**: Click "Map" to see spots plotted geographically.
-   **Add Spot**: Log in and click "Post Spot" to share a new location.
-   **Admin**: Access `http://127.0.0.1:8000/manage/` (custom dashboard) or `http://127.0.0.1:8000/admin/` (standard Django admin) using your superuser credentials.

## Deployment Configuration

### Environment Variables

When deploying to production (e.g., Render.com), set the following environment variables:

#### Required Django Settings
-   `SECRET_KEY`: A random string for cryptographic signing.
-   `DEBUG`: Set to `false` in production.
-   `DATABASE_URL`: Connection string for the PostgreSQL database.

#### Automatic Superuser Creation
To automatically create an admin account upon deployment:

-   `DJANGO_SUPERUSER_USERNAME`: Admin username (e.g., `admin`)
-   `DJANGO_SUPERUSER_EMAIL`: Admin email
-   `DJANGO_SUPERUSER_PASSWORD`: Admin password

### Deployment Files

-   `post_deploy.sh`: Runs after deployment to apply migrations and create a superuser.
-   `start.sh`: Main entry point script for starting the Gunicorn server.
-   `travel_log_map/`: Project configuration directory.
-   `spots/`: Main application directory.

## Tech Stack

-   **Backend**: Django 5.2+
-   **Database**: PostgreSQL (Production), SQLite (Development)
-   **Deployment**: Render.com
-   **Server**: Gunicorn
-   **Static Files**: WhiteNoise

## License

This project is private and does not grant a license for public use.
