from .base import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Security settings (minimal; extend as needed)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=False)
