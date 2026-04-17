# Insighters Inc Workflow Automation

Django application for collecting business and individual intake data, generating completed intake PDFs, syncing submissions to monday.com, and managing short-lived client intake credentials from an admin dashboard.

## Tech Stack

- Python 3.11
- Django 4.2
- PostgreSQL through `DATABASE_URL`
- django-allauth with Microsoft OAuth
- Microsoft Graph `Mail.Send` for credential and submission emails
- monday.com GraphQL API for submission tracking and PDF uploads
- pypdf for filling PDF form templates
- Bootstrap 5 / django-bootstrap5 templates
- Docker, Google Cloud Build, Google Cloud Run, Cloud SQL, Artifact Registry, Secret Manager, and WhiteNoise for production deployment

## Current Functionality

### Public and Client Pages

- `/` - Home page.
- `/intake-login/` - Client intake login.
- `/business/` - Business intake form. Requires intake login.
- `/individual/` - Individual intake form. Requires intake login.
- `/submission-processing/` - Post-submit processing page that completes monday.com sync and file upload.

### Admin Pages

- `/admin-login/` - Microsoft sign-in entry page for admins.
- `/dashboard/` - Admin dashboard for generating temporary client credentials.
- `/admin/` - Django admin.
- `/accounts/` - django-allauth Microsoft OAuth routes.

### Intake Credential Flow

- Admins sign in through Microsoft OAuth.
- The dashboard creates temporary credentials for either the business or individual intake form.
- Credentials are form-scoped, expire after five days, and are marked used after a successful client submission.
- Generated passwords are hashed before storage.
- Expired credentials are deleted when the dashboard loads.
- `INTAKE_LOGIN_ID` and `INTAKE_LOGIN_PASSWORD` can be set as a local/testing bypass.

### Submission Flow

- Business and individual forms validate user input, then save non-sensitive submission data to the database.
- SSNs and bank account numbers are accepted for validation/PDF generation but are not stored in database models.
- A completed PDF is generated from the matching template in `src/apps/core/pdf_templates/`.
- Submission data and the generated PDF path are staged in the session.
- `/submission-processing/` creates or updates the monday.com item, uploads the generated PDF to the configured monday file column, and clears the intake session once sync succeeds.
- A confirmation email can be sent to the admin who created the credential.

### Email Flow

- Credential emails are sent from the signed-in admin's Microsoft account with Microsoft Graph.
- `src/templates/email_temp.html` is used for credential emails.
- `src/templates/email_confirmation.html` is used for completion confirmation emails.
- Microsoft tokens are stored by django-allauth. If an admin does not have a Microsoft token, the dashboard warns that email sending will fail until the admin signs in through Microsoft.

### monday.com Integration

- The app creates monday.com items using the configured board and group IDs.
- Email and phone values are formatted for monday.com column types.
- Business and individual submissions can use separate group IDs and column maps.
- Generated PDFs are uploaded to the configured monday file column.
- `tests/test_monday.py` verifies a development monday token and board when `DEV_MONDAY_API` and `DEV_MONDAY_BOARD_ID` are set.

## Repository Structure

- `manage.py` - Django management entry point. Defaults to `src.config.settings.local`.
- `requirements.txt` - Python runtime dependencies.
- `src/config/` - Django project configuration, URL routing, ASGI, WSGI, and settings.
- `src/config/settings/base.py` - Shared settings, installed apps, authentication, session settings, static files, database configuration, monday.com settings, Microsoft OAuth settings, and sensitive exception filter registration.
- `src/config/settings/local.py` - Local development overrides.
- `src/config/settings/production.py` - Production overrides, Google Secret Manager loading, security headers/cookies, WhiteNoise, and log redaction.
- `src/apps/core/` - Main Django app containing forms, models, routes, views, email helpers, PDF generation, PDF field mapping, error filters, migrations, and app-specific tests.
- `src/apps/core/pdf_templates/` - Source PDF templates: `BusinessForm.pdf` and `IndividualForm.pdf`.
- `src/templates/` - HTML templates for the home page, admin pages, intake login, intake forms, processing page, and email bodies.
- `src/static/` - Static assets such as logo, background image, Microsoft icon, and email preview HTML.
- `generated_forms/` - Runtime output folder for generated business and individual PDFs.
- `staticfiles/` - Collected static output for deployment. Ignored by git.
- `tests/` - Integration-style pytest tests that exercise running app pages, auth flow, form submission, database persistence, Docker reachability, and monday.com connectivity.
- `src/apps/core/tests/` - Django form unit tests plus test notes.
- `documentation/` - Project documentation PDFs, including user guide and deployment/architecture documentation.
- `scripts/entrypoint.sh` - Container entrypoint that runs `collectstatic` before starting the container command.
- `scripts/init_gcp.sh` - One-time helper for enabling GCP APIs and creating the Artifact Registry repository.
- `Dockerfile` - Production-style container image for Cloud Run/Gunicorn.
- `docker-compose.yml` - Local Docker stack with the Django web container and PostgreSQL.
- `compose.debug.yaml` - Debug container override with `debugpy`.
- `cloudbuild.yaml` - Cloud Build pipeline for building, pushing, migrating, and deploying to Cloud Run.
- `.dockerignore` - Excludes local, test, Docker, and secret files from container build context.
- `.gitignore` - Excludes local environments, generated static output, caches, `.env`, and PDF artifacts.
- `.gitattributes` - Git attributes.
- `.gitkeep` - Placeholder file.
- `gunicorn.conf.py` - Reserved Gunicorn config file. Currently empty because the Docker `CMD` supplies Gunicorn options.

## Core App Files

- `src/apps/core/forms.py` - Defines business intake, personal intake, client login, and credential creation forms. Includes validators for SSNs, ZIP codes, phone numbers, FINs, ranges, dates, and certification fields.
- `src/apps/core/models.py` - Defines `BusinessIntakeSubmission`, `PersonalIntakeSubmission`, and `TemporaryIntakeCredential`.
- `src/apps/core/views.py` - Handles page rendering, intake login, credential generation, form submission, PDF generation, Microsoft email calls, monday.com item creation, monday.com file upload, and session cleanup.
- `src/apps/core/email.py` - Sends credential and submission confirmation emails through Microsoft Graph.
- `src/apps/core/pdf_engine.py` - Fills PDF templates with pypdf and writes generated files under `generated_forms/`.
- `src/apps/core/pdf_mapping.py` - Maps cleaned Django form data to PDF field names and checkbox markers.
- `src/apps/core/error_filters.py` - Redacts sensitive POST fields in Django exception reports.
- `src/apps/core/urls.py` - Core app route definitions.
- `src/apps/core/migrations/` - Database schema migrations through `0007_test_cicd_pipeline.py`.

## Data Models

- `BusinessIntakeSubmission` - Stores business owner names, business contact details, business history, financial history, accounting period, bank metadata, payroll IDs, and sales tax IDs. SSNs and bank account numbers are not stored.
- `PersonalIntakeSubmission` - Stores filing details, client/spouse information, contact information, filing status, dependent metadata, income/expense selections, and certification signature. SSNs are not stored.
- `TemporaryIntakeCredential` - Stores one-time login credentials for a specific intake form, including hashed password, client email, creator, expiration time, and used time.

## Environment Variables

The app reads `.env` from the repository root through `django-environ`.

### Required for Normal Operation

- `DATABASE_URL` - Database connection string. Local settings default to SQLite at `/tmp/db.sqlite3` if this is not set, but Docker and production expect PostgreSQL.
- `DJANGO_SECRET_KEY` - Django secret key.
- `BASE_URL` - Public base URL used in emailed form links.

### Local/Test Bypass

- `INTAKE_LOGIN_ID` - Optional client intake login bypass.
- `INTAKE_LOGIN_PASSWORD` - Optional client intake password bypass.

### Django and Security

- `DEBUG`
- `ALLOWED_HOSTS`
- `SECURE_SSL_REDIRECT`
- `SECURE_HSTS_SECONDS`
- `SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `SECURE_HSTS_PRELOAD`

### Microsoft OAuth and Email

- `ENTRA_CLIENT_ID`
- `ENTRA_CLIENT_SECRET`
- `ENTRA_TENANT_ID`

### monday.com

- `MONDAY_API`
- `MONDAY_API_URL`
- `MONDAY_FILE_API_URL`
- `MONDAY_API_VERSION`
- `MONDAY_BOARD_ID`
- `DEV_MONDAY_API`
- `DEV_MONDAY_BOARD_ID`

### Google Cloud

- `GOOGLE_CLOUD_PROJECT`
- `DATABASE_CONNECTION_NAME`

### Legacy/Unused Settings Still Present

- `SHAREFILE_CLIENT_ID`
- `SHAREFILE_API`
- `SHAREFILE_URI`

## Google Secret Manager

`src/config/settings/production.py` can load these Secret Manager secrets:

- `DJANGO_SECRET_KEY`
- `DATABASE_URL`
- `ENTRA_CLIENT_SECRET`
- `ENTRA_CLIENT_ID`
- `ENTRA_TENANT_ID`
- `MONDAY_API`
- `MONDAY_BOARD_ID`

Production settings also redact fetched secrets, SSNs, emails, and bearer tokens from console logs.

## Local Development

### Python

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open `http://localhost:8000/`.

### Docker

```powershell
docker compose up --build
```

Open `http://localhost:8000/`. Stop the stack with:

```powershell
docker compose down
```

Reset the local database volume with:

```powershell
docker compose down -v
```

## Running Tests

The `src/apps/core/tests/` tests are Django tests:

```powershell
python manage.py test
python manage.py test src.apps.core.tests
```

The root `tests/` suite is pytest-based and expects a running server. By default it uses `BASE_URL=http://localhost:8000`.

```powershell
pytest
```

Useful environment variables for the pytest suite:

- `BASE_URL` - Running app URL.
- `DATABASE_URL` - Required for database persistence tests.
- `INTAKE_LOGIN_ID` and `INTAKE_LOGIN_PASSWORD` - Required for intake-login tests.
- `DEV_MONDAY_API` and `DEV_MONDAY_BOARD_ID` - Required for the monday.com connectivity test; otherwise that test is skipped.

## Deployment

### Cloud Build and Cloud Run

`cloudbuild.yaml` performs these steps:

1. Build the Docker image.
2. Push the image to Artifact Registry.
3. Run `python manage.py migrate --noinput` through the App Engine exec wrapper and Cloud SQL connection.
4. Deploy the image to Cloud Run with production settings, Cloud SQL, and runtime environment variables.

Default substitutions:

- `_REGION=us-central1`
- `_REPO_NAME=insighters-repo`
- `_SERVICE_NAME=insighters-workflow-automation`
- `_DB_CONNECTION_NAME=insighters-app:us-central1:insighters-prod-db`

### GCP Initialization

`scripts/init_gcp.sh` is a one-time setup helper. It signs in with `gcloud`, enables required APIs, and creates the Artifact Registry repository if it does not already exist.

Do not run `scripts/init_gcp.sh` inside CI/CD.

## Generated Files and Static Files

- Generated PDFs are written under `generated_forms/business/` and `generated_forms/individual/`.
- `staticfiles/` is created by `collectstatic`.
- Runtime PDFs and collected static files should not be committed.

## Security Notes

- SSNs are accepted in form submissions for validation and PDF generation but are not stored in database models.
- Business bank account numbers are accepted in form submissions for validation/PDF generation but are not stored in database models.
- Temporary intake passwords are shown once and stored only as hashes.
- Sensitive POST parameters are scrubbed by `GlobalSensitiveDataFilter`.
- Production logs also apply a dynamic redaction filter for known secrets, SSNs, emails, and bearer tokens.
- Admin email sending depends on Microsoft OAuth tokens stored by django-allauth.

## Known Limitations and In-Progress Areas

- Generated PDFs are stored on the application filesystem before monday.com upload; Cloud Run filesystem storage is ephemeral.
- Temporary credential cleanup runs when the dashboard loads, not from a scheduled job.
- monday.com group IDs, file column IDs, and some column maps are currently configured in settings code.
- `send_submission_confirmation_email` supports PDF attachments, but current form views do not pass the generated PDF path into that function.
- `gunicorn.conf.py` is currently empty.
- `SHAREFILE_*` settings remain in configuration but are not used by the current flow.
