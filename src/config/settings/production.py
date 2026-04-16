# File Usage: To override the defaults set in base.py to ensure the application is secure, performant, 
# and observable when running on infrastructure like Google Cloud Run.

from .base import *
from google.cloud import secretmanager
import json
import re
import logging
from django.views.decorators.debug import sensitive_variables

KNOWN_SECRETS = set()

class DynamicSecretFilter(logging.Filter):
    def filter(self, record):
        log_message = record.getMessage()
        
        # 1. Exact Match Redaction (The GSM Secrets)
        # If any fetched secret exists in the log message, replace it entirely.
        for secret in KNOWN_SECRETS:
            if secret in log_message:
                log_message = log_message.replace(secret, '[REDACTED_GCP_SECRET]')

        # 2. Regex Fallback (For PII and dynamically generated tokens)
        # Redact SSNs
        log_message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED SSN]', log_message)
        # Redact Emails
        log_message = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED EMAIL]', log_message)
        # Catch standard OAuth Bearer tokens just in case
        log_message = re.sub(r'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+', 'Bearer [REDACTED_TOKEN]', log_message)

        record.msg = log_message
        record.args = () 
        return True

# Production settings
DEBUG = False

client = secretmanager.SecretManagerServiceClient()
# Function to fetch secret from Google Secret Manager
@sensitive_variables('response', 'project_id', 'name')
def get_secret(secret_id: str, version_id: str = "latest") -> str:
    """Fetch a secret from Google Cloud Secret Manager."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not project_id:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable must be set.")
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"
    response = client.access_secret_version(name=name)
    secret_value = response.payload.data.decode("UTF-8")
    
    if len(secret_value) > 5:
        KNOWN_SECRETS.add(secret_value)
        
    return secret_value

# Map Django settings (keys) to Google Secret Manager IDs (values)
SECRETS_MAPPING = {
    "SECRET_KEY": "DJANGO_SECRET_KEY",
    "DATABASE_URL_VAL": "DATABASE_URL",  # Fetch into temp var, apply to DATABASES below
    "MICROSOFT_CLIENT_SECRET": "ENTRA_CLIENT_SECRET",
    "MICROSOFT_CLIENT_ID": "ENTRA_CLIENT_ID",
    "MICROSOFT_TENANT_ID": "ENTRA_TENANT_ID",
    "MONDAY_API_TOKEN": "MONDAY_API",
    "MONDAY_BOARD_ID": "MONDAY_BOARD_ID",
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

# --- Post-Fetch Configuration Application ---
# Because base.py runs first, complex dictionaries (DATABASES, SOCIALACCOUNT_PROVIDERS)
# are already built using the old/empty Env values. We must update them now.

if "DATABASE_URL_VAL" in globals():
    # Re-configure database using the URL fetched from Secret Manager
    DATABASES['default'] = environ.Env.db_url_config(globals()["DATABASE_URL_VAL"])

if "MICROSOFT_CLIENT_SECRET" in globals():
    # Update the AllAuth provider config with the fetched secret
    SOCIALACCOUNT_PROVIDERS['microsoft']['APP']['secret'] = globals()["MICROSOFT_CLIENT_SECRET"]

if "MICROSOFT_CLIENT_ID" in globals():
    SOCIALACCOUNT_PROVIDERS['microsoft']['APP']['client_id'] = globals()["MICROSOFT_CLIENT_ID"]
    
if "MICROSOFT_TENANT_ID" in globals():
    SOCIALACCOUNT_PROVIDERS['microsoft']['TENANT'] = globals()["MICROSOFT_TENANT_ID"]

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
    'filters': {
        'sensitive_data_filter': {
            '()': DynamicSecretFilter,
        }
    },
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
            'filters': ['sensitive_data_filter'],  # <-- Inject the filter here
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
