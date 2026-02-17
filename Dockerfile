# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group to run the application
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

# Set work directory
WORKDIR /app

# Install system dependencies
# libpq-dev and gcc are required for building psycopg2 and other python extensions
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Change ownership of the application files to the non-root user
RUN chown -R appuser:appgroup /app

# Make the entrypoint script executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose port 8080 (Google Cloud Run default)
EXPOSE 8080

# Switch to the non-root user
USER appuser

# Set the entrypoint to run migrations before starting the server
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Run gunicorn
# We point to src.config.wsgi based on your project structure in README.md
# Workers and threads are tuned for a standard container environment
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--threads", "8", "--timeout", "0", "src.config.wsgi:application"]
