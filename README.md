# HealthBridge

HealthBridge is a simple Django web application for managing patient registration, medical records, consultations, follow-ups, and prescriptions.

## Project Structure

- `manage.py` - Django management script used to run commands like migrations and the development server.
- `healthbridge/` - Main Django project configuration.
  - `settings.py` - Project settings and installed apps.
  - `urls.py` - URL routing configuration.
  - `wsgi.py` / `asgi.py` - Deployment entry points.
- `registration/` - Main application for healthcare management.
  - `models.py` - Database models for Patient, MedicalRecord, Consultation, FollowUp, and Prescription.
  - `forms.py` - Forms for creating and updating records.
  - `views.py` - Views for handling user requests and rendering templates.
  - `urls.py` - App-specific routes.
  - `templates/registration/` - HTML templates used for rendering pages.

## Requirements

Install Python and pip, then install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Setup

1. Navigate to the project directory:

```bash
cd d:\dummy_projects\sahil\HealthBridge
```

2. Apply database migrations:

```bash
python manage.py migrate
```

3. (Optional) Create a superuser to access the Django admin site:

```bash
python manage.py createsuperuser
```

## Run the Project

Start the Django development server:

```bash
python manage.py runserver
```

Then open your browser at `http://127.0.0.1:8000/`.

## Notes

- The default database is SQLite and is stored in `db.sqlite3`.
- Static files are served automatically by Django when `DEBUG = True`.
- This project uses Django 6.0.6 as specified in `requirements.txt`.
