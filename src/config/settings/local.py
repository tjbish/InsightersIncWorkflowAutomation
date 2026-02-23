from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Allow any host for local development
ALLOWED_HOSTS = ['*']

# Print emails to console instead of sending
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'