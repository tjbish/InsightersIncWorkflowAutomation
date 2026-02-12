# File Usage: To override the defaults set in base.py to ensure the application is secure, performant, 
# and observable when running on infrastructure like Google Cloud Run.

from .base import *
from google.cloud import secretmanager

# Production settings
DEBUG = False

# Function to fetch secret from Google Secret Manager
def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """Fetch a secret from Google Cloud Secret Manager."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set.")

    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    return response.payload.data.decode("UTF-8")

# Map Django settings (keys) to Google Secret Manager IDs (values)
SECRETS_MAPPING = {
    "SECRET_KEY": "DJANGO_SECRET_KEY",
    "SHAREFILE_API": "SHAREFILE_API",
    "MONDAY_API": "MONDAY_API",
    "SHAREFILE_CLIENT_ID": "SHAREFILE_CLIENT_ID",
    "SHAREFILE_URI": "SHAREFILE_URI",
}

for setting_name, secret_id in SECRETS_MAPPING.items():
    try:
        globals()[setting_name] = get_secret(secret_id)
    except Exception as e:
        print(f"Warning: Could not fetch {secret_id} for {setting_name} from Secret Manager: {e}")
        
        # Critical check: If SECRET_KEY failed to load from GSM, ensure it exists in env
        if setting_name == "SECRET_KEY":
            # Check if base.py successfully found a key in the environment (using the name from base.py), otherwise fail
            if env('DJANGO_SECRET_KEY', default=None) is None:
                 raise RuntimeError(f"CRITICAL: SECRET_KEY is missing! Failed to fetch from Secret Manager and not found in environment.")


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
