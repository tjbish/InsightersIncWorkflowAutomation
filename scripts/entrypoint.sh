#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Collect static files for non-debug deployments
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the command passed to the container (e.g., gunicorn or runserver)
exec "$@"
