# Entrypoint for Gunicorn server

import os
from django.core.wsgi import get_wsgi_application

# Default to production settings, but this is usually overridden by env vars
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.settings.production')

application = get_wsgi_application()
