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

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# TODO: Remove default once temp IDs can be generated
INTAKE_LOGIN_ID = env('INTAKE_LOGIN_ID', default='admin')
INTAKE_LOGIN_PASSWORD = env('INTAKE_LOGIN_PASSWORD', default='admin')
ADMIN_LOGIN_ID = env('ADMIN_LOGIN_ID', default='admin')
ADMIN_LOGIN_PASSWORD = env('ADMIN_LOGIN_PASSWORD', default='admin')

# Third Party API Settings
SHAREFILE_CLIENT_ID = env('SHAREFILE_CLIENT_ID', default=None)
SHAREFILE_API = env('SHAREFILE_API', default=None)
SHAREFILE_URI = env('SHAREFILE_URI', default=None)
MONDAY_API = env('MONDAY_API', default=None)

INSTALLED_APPS = [
    # Sprint 2; make sure to check if we need or don't need admin rights
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'django_bootstrap5',
    # 'django_htmx', # Uncomment if using HTMX
    # Local apps
    'src.apps.core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django_htmx.middleware.HtmxMiddleware', # Uncomment if using HTMX
]

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
    'default': env.db(),
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
