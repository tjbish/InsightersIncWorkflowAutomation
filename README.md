# All files short explanation
    Root Files:
        README.md – High-level overview of the project, setup instructions, and deployment notes for Google Cloud.

        .gitignore – Specifies files and directories that should not be tracked by Git (virtual envs, secrets, build artifacts).

        .dockerignore – Excludes unnecessary files from the Docker build context to keep images small and secure.

        manage.py – Django’s command-line utility for administrative tasks such as running the server and migrations.

        requirements.txt – Lists all Python dependencies required to run the application in any environment.

        gunicorn.conf.py – Configuration file defining Gunicorn runtime settings for production deployment.

        Dockerfile – Defines how the Django application is containerized for deployment on Google Cloud.

        cloudbuild.yaml – Describes the CI/CD pipeline steps used by Google Cloud Build to build and deploy the app.

        app.yaml – Google App Engine configuration specifying runtime, environment variables, and service settings.

    Django project config:
        src/config/__init__.py – Marks the config directory as a Python package.

        src/config/urls.py – Defines the URL routing table that maps request paths to Django views.

        src/config/wsgi.py – Entry point for WSGI-compatible servers to serve the Django application.

        src/config/asgi.py – Entry point for ASGI-compatible servers supporting async features.

        src/config/settings/ – Contains environment-specific Django configuration modules.

    Settings files:
        src/config/settings/__init__.py – Marks the settings directory as a Python package.

        src/config/settings/base.py – Holds shared Django settings common to all environments.

        src/config/settings/local.py – Overrides base settings for local development and debugging.

        src/config/settings/production.py – Overrides base settings with security and performance settings for production.

    Django apps:
        src/apps/ – Container directory for all Django applications used by the project.

        src/apps/exampleApp.py - An example app placeholder to ensure correct folder structure.

        src/apps/core/ – Primary application containing core business logic and views.

    Templates & static assets:
        templates/ – Stores Django HTML templates used to render dynamic pages.

        src/static/ – Holds static files such as CSS, JavaScript, and images collected for deployment.

    Scripts:
        scripts/ – Contains helper scripts used during container startup and deployment.

        scripts/entrypoint.sh – Runs database migrations, static collection, and starts the application server.

        scripts/deploy.sh – Automates deployment commands to Google Cloud services.

        scripts/init_gcp.sh - Initializes the GCP project.
    
    Tests:
        tests/ – Contains automated tests used to verify application correctness and prevent regressions.

    GraphQLQueryExample: (See monday-client-writer (GraphQLQuery.py) section below)
        GraphQLQueryExample/config.json - Contains configuration information for a sample GraphQLQuery python pipeline program.
        GraphQLQueryExample/GraphQLQuery.py - Python code template for sending read and update queries to/from a GraphQL API (Monday.com).

# Google Cloud Information
    OPTIONAL FILES: 
    - gunicorn.conf.py  (Cloud Run)
    - cloudbuild.yaml   (Cloud Build CI/CD)
    - app.yaml          (App Engine Standard/Flex)

    WE MAY KEEP ONE OR ALL OF THE ABOVE DEPENDING ON GOOGLE CLOUD DEPLOYMENT IMPLEMENTATION


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

# Core app
    The minimal core app now renders a template-based home page at `/`.
    Template file: `templates/home.html`

    Intake pages:
        - Business intake: `/business/`
        - Individual intake: `/individual/`
        - Intake login: `/intake-login/`

    Intake access control:
        - Business and Individual intake pages require login.
        - Temporary credentials are controlled by `INTAKE_LOGIN_ID` and `INTAKE_LOGIN_PASSWORD`.

    Admin pages
        - Admin Login: `/admin-login/`
        - Admin Dashboard: `/dashboard/` 
