#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations automatically
echo "Applying database migrations..."
python manage.py migrate --noinput

# Execute the command passed to the container (e.g., gunicorn or runserver)
exec "$@"
