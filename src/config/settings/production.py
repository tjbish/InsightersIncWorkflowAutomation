# File Usage: To override the defaults set in base.py to ensure the application is secure, performant, 
# and observable when running on infrastructure like Google Cloud Run.

from .base import *

# Production settings
DEBUG = False

# Raise error if SECRET_KEY is missing in production
if env('SECRET_KEY', default=None) is None:
    raise RuntimeError("SECRET_KEY is missing in production environment!")

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# HSTS Settings (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = env.int('SECURE_HSTS_SECONDS', default=31536000)  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool('SECURE_HSTS_INCLUDE_SUBDOMAINS', default=True)
SECURE_HSTS_PRELOAD = env.bool('SECURE_HSTS_PRELOAD', default=True)

# Static Files (WhiteNoise)
# We inject WhiteNoise middleware after SecurityMiddleware for efficient serving
try:
    # Find index of SecurityMiddleware to insert after it
    security_index = MIDDLEWARE.index('django.middleware.security.SecurityMiddleware')
    MIDDLEWARE.insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
except ValueError:
    # If SecurityMiddleware is missing, insert at the top
    MIDDLEWARE.insert(0, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging (Log to console for Cloud Logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# CSRF Trusted Origins (Required for Django 4.0+ behind https proxy)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
