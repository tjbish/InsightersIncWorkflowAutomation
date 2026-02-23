# Insighters Inc Workflow Automation

Django application for collecting business and individual intake data with gated client access and an admin dashboard for generating temporary intake credentials.

## Tech Stack

- Python 3
- Django 4.2
- PostgreSQL via `DATABASE_URL`
- Bootstrap 5 templates
- Google Secret Manager support for production
- Optional Docker / Google Cloud deployment files included

## Repository Structure

- `src/apps/core/` - Main app (forms, views, models, routes, tests)
- `src/templates/` - HTML templates (`home`, `admin`, login pages, intake forms)
- `src/static/` - Static assets (logo/background)
- `src/config/settings/` - `base.py`, `local.py`, `production.py`
- `GraphQLQueryExample/` - Example standalone monday.com GraphQL script
- `docker-compose.yml`, `Dockerfile`, `app.yaml`, `cloudbuild.yaml` - Container/deployment support

## Current Application Functionality

### Routes

- `/` - Home page
- `/business/` - Business intake form (requires intake login)
- `/individual/` - Personal intake form (requires intake login)
- `/intake-login/` - Client intake login page
- `/admin-login/` - Admin login page
- `/dashboard/` - Admin dashboard (requires admin login)
- `/admin/` - Django admin

### Access Control and Login Flow

- Business and individual intake pages are protected by `@require_intake_login`.
- Client intake login validates against `TemporaryIntakeCredential` records in the database.
- Temporary credentials are:
  - Form-scoped (`business` or `individual`)
  - Expiration-based (`expires_at`)
  - One-time use (`used_at` is set on successful login)
- Admin dashboard is protected by `@require_admin_login`.
- Admin login currently validates using environment variables `ADMIN_LOGIN_ID` and `ADMIN_LOGIN_PASSWORD`.

### Admin Dashboard (Credential Generation)

From `/dashboard/`, admin can generate a temporary login for:

- Business intake
- Individual intake

Generation behavior:

- Creates unique login ID (`INT-XXXXXXXX` style)
- Creates random password (shown once in UI)
- Stores hashed password (`make_password`) in DB
- Stores `client_email`, `form_type`, `created_by_login_id`, `expires_at`
- Cleans up expired temporary credentials every time dashboard is accessed

### Intake Data Capture

#### Business Intake

Saved to `BusinessIntakeSubmission`.

- SSNs are accepted/validated in form but not stored.
- Bank account number is accepted/validated but not stored.

#### Personal Intake

Saved to `PersonalIntakeSubmission`.

- SSNs are accepted/validated in form but not stored.
- Multi-select fields are stored as comma-separated strings.

### Form Validation

Forms include validation for:

- SSN format (`XXX-XX-XXXX`)
- ZIP code format
- Phone number format
- Numeric ranges (ownership %, months in home, etc.)
- Required certification/signature fields for personal intake

## Data Models (Core)

- `BusinessIntakeSubmission`
- `PersonalIntakeSubmission`
- `TemporaryIntakeCredential`

Migrations currently present:

- `0001_initial.py`
- `0002_temporaryintakecredential.py`

## Environment Variables

Configured in `src/config/settings/base.py` and `src/config/settings/production.py`.

### Required

- `DATABASE_URL`

### Common

- `DJANGO_SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `ADMIN_LOGIN_ID`
- `ADMIN_LOGIN_PASSWORD`

### Optional Third-Party

- `SHAREFILE_CLIENT_ID`
- `SHAREFILE_API`
- `SHAREFILE_URI`
- `MONDAY_API`

### Production Secret Manager

`production.py` can pull secrets from Google Secret Manager using:

- `GOOGLE_CLOUD_PROJECT`

Secret mapping is defined in `SECRETS_MAPPING`.

## Local Development

1. Create and activate a virtual environment.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Create `.env` at repository root and set at least `DATABASE_URL`.
4. Run migrations:
   - `python manage.py migrate`
5. Start server:
   - `python manage.py runserver`

## Running Tests

Core form tests exist in:

- `src/apps/core/tests/test_business_forms.py`
- `src/apps/core/tests/test_personal_forms.py`

Run all tests:

- `python manage.py test`

Run only core tests:

- `python manage.py test src.apps.core.tests`

## Deployment Notes

This repo includes deployment artifacts for Google Cloud and containers:

- `Dockerfile`
- `docker-compose.yml`
- `app.yaml`
- `cloudbuild.yaml`
- `gunicorn.conf.py`

Choose the files relevant to your deployment target (Cloud Run, App Engine, etc.).

## Known Limitations / In-Progress Areas

- Admin authentication is still environment-variable based (not DB-backed users).
- Temporary credential cleanup currently runs on dashboard access (not scheduled worker/cron).
- Some TODOs remain in form/security comments for additional hardening.

# Local development (Django)
    This project uses environment variables loaded from a `.env` file at the repo root.
    A template is provided as `.env.example` (copy it to `.env` for local use).

    ## Required environment variables
        - DATABASE_URL (required, no sqlite fallback configured)
        - DJANGO_SETTINGS_MODULE (optional; defaults to src.config.settings.local in manage.py)
        - SECRET_KEY (optional for local; defaults in local settings)
        - DEBUG (optional for local; defaults in local settings)

    ## Additional environment variables
        - INTAKE_LOGIN_ID (optional; defaults to admin)
        - INTAKE_LOGIN_PASSWORD (optional; defaults to admin)

    ## Quick start (local, non-Docker)
        1. Create/activate a virtualenv and install deps:
           - python -m venv .venv
           - .\.venv\Scripts\activate
           - pip install -r requirements.txt

        2. Create .env (copy from .env.example) and set DATABASE_URL.

        3. Run migrations and start the server:
           - python manage.py migrate
           - python manage.py runserver

    ## Quick start (Docker)
        1. Build and start services:
           - docker compose up --build
        2. Open the app:
           - http://localhost:8000/ (admin at /admin/)
        3. Stop services:
           - docker compose down
        4. Reset database volume (optional):
           - docker compose down -v

# monday-client-writer (GraphQLQuery.py)

        A simple Python CLI program that creates a new client item on a monday.com board and writes client info into columns using monday’s GraphQL API.

        ## What this does

        When you run the script, it will:
        1. Read `config.json` (API token, board ID, group ID, column IDs, defaults)
        2. Create a new item (row) in your monday board (item name = client name)
        3. Update columns like email, phone, company, and notes (optional)

        ---

        ## Requirements

        - Python 3.9+ recommended
        - A monday.com API token
        - A board ID and group ID you want to write items into
        - Column IDs for email/phone/company/notes on your board

        ---

        ## Setup

        ### 1 Install dependencies

        ```bash
        pip install requests
        ```