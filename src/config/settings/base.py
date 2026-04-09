from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# We are in src/config/settings/base.py, so we go up 4 levels to get to root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

env = environ.Env()
# Read .env file if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-fallback-key')

DEBUG = env.bool('DEBUG', default=False)

# The base URL for building absolute links in emails, etc.
BASE_URL = env('BASE_URL', default='http://localhost:8000')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = [
    "https://insighters-workflow-automation-428824878696.us-central1.run.app",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

INTAKE_LOGIN_ID = env('INTAKE_LOGIN_ID', default=None)
INTAKE_LOGIN_PASSWORD = env('INTAKE_LOGIN_PASSWORD', default=None)

# Third Party API Settings
# Delete Sharefile API keys
SHAREFILE_CLIENT_ID = env('SHAREFILE_CLIENT_ID', default=None)
SHAREFILE_API = env('SHAREFILE_API', default=None)
SHAREFILE_URI = env('SHAREFILE_URI', default=None)

# Production keys & ID mappings
MONDAY_API_TOKEN = env('MONDAY_API', default=None)
MONDAY_API_URL = env('MONDAY_API_URL', default='https://api.monday.com/v2')
MONDAY_API_VERSION = env('MONDAY_API_VERSION', default='2024-04')
MONDAY_BOARD_ID = env('MONDAY_BOARD_ID', default=None)
MONDAY_BUSINESS_GROUP_ID = "group_mm262dz"
MONDAY_PERSONAL_GROUP_ID = "topics"
MONDAY_FILE_ID = "file_mm1nffry"
MONDAY_BUSINESS_COLUMN_MAP = {"email":"email_mm26e82x", "phone_number":"phone_mm26ghe3"}
MONDAY_PERSONAL_COLUMN_MAP = {"email":"email_mm26e82x", "phone_number":"phone_mm26ghe3", "date_signed":"date4"}

# Dev keys & ID mappings
DEV_MONDAY_API_TOKEN = env('MONDAY_DEV_API', default=None)
DEV_MONDAY_BOARD_ID = env('MONDAY_DEV_BOARD_ID', default=None)
DEV_MONDAY_BUSINESS_GROUP_ID = "topics"
DEV_MONDAY_PERSONAL_GROUP_ID = "group_title"
DEV_MONDAY_FILE_ID = "file_mm26rrdp"
DEV_MONDAY_BUSINESS_COLUMN_MAP = {"email":"email_mm27w5wx", "phone_number":"phone_mm27rk8x"}
DEV_MONDAY_PERSONAL_COLUMN_MAP = {"email":"email_mm27w5wx", "phone_number":"phone_mm27rk8x", "date_signed":"date4"}

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',  # Required by allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.microsoft',
    # Third party
    'django_bootstrap5',
    # Local apps
    'src.apps.core',
]

# allauth requires a site ID
SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]


MICROSOFT_CLIENT_ID = env('ENTRA_CLIENT_ID', default=None)
MICROSOFT_CLIENT_SECRET = env('ENTRA_CLIENT_SECRET', default=None) # Prod Expires in 180 days (Oct. 1 2026)
MICROSOFT_TENANT_ID = env('ENTRA_TENANT_ID', default=None)


SOCIALACCOUNT_PROVIDERS = {
    'microsoft': {
        'TENANT': MICROSOFT_TENANT_ID,
        'APP': {
            'client_id': MICROSOFT_CLIENT_ID,
            'secret': MICROSOFT_CLIENT_SECRET,
        },
        'SCOPE': [
            'User.Read',
            'Mail.Send',
            'offline_access',
        ],
        'AUTH_PARAMS': {
            'prompt': 'select_account',
            'access_type': 'offline',
        },
    }
}

# Recommended allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
LOGIN_REDIRECT_URL = '/dashboard'  # Where to send the admin after a successful login
LOGIN_URL = '/admin/login/'
ACCOUNT_LOGOUT_REDIRECT_URL = '/'
ACCOUNT_LOGOUT_ON_GET = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_STORE_TOKENS = True
SOCIALACCOUNT_ADAPTER = 'allauth.socialaccount.adapter.DefaultSocialAccountAdapter'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ACCOUNT_EMAIL_VERIFICATION = 'none'

# Session Security Settings
SESSION_COOKIE_AGE = 3600  # Session expires after 1 hour
SESSION_SAVE_EVERY_REQUEST = True  # Reset the expiration timer on every request (idle timeout)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Ensure session ends if the browser is closed

ROOT_URLCONF = 'src.config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'src' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'src.config.wsgi.application'

# Database
# This reads the DATABASE_URL environment variable set in docker-compose.yml
DATABASES = {
    'default': env.db('DATABASE_URL', default='sqlite:///tmp/db.sqlite3'),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'src' / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Enforce global scrubbing of sensitive POST data on crash reports
DEFAULT_EXCEPTION_REPORTER_FILTER = 'src.apps.core.error_filters.GlobalSensitiveDataFilter'
