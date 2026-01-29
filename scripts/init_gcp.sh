#!/bin/bash
# scripts/init_gcp.sh

# This script initalizes the GCP project.
# Before running, make sure to chmod +x the script to enable execution 

# NOTE: Please do not include in CI/CD pipeline as this is just for init. If any CI/CD pipeline
# are created, please put in code to exclude form build process.

set -e  # exit immediately if a command exits with an error

# authenticate user
echo "Authenticating with Google Cloud:"
# NOTE: This command is interactive and requires a browser.
# If running in a CI/CD pipeline (e.g., GitHub Actions), remove this line
# and authenticate using a Service Account instead.
gcloud auth login

# dynamically fetch gcp project name and region
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)

# Use REGION variable if set by user already, otherwise try gcloud config, else default to us-central1
REGION=${REGION:-$(gcloud config get-value compute/region 2>/dev/null)}
REGION=${REGION:-us-central1}

# config variable
REPO_NAME="insighters-repo"      # name of Docker storage folder on cloud for cloud images

if [ -z "$PROJECT_ID" ]; then
  echo "Error: No project selected. Please run 'gcloud config set project [YOUR_PROJECT_ID]' first."
  exit 1
fi

echo " ----------------------------------------------"
echo "  Starting Infrastructure Setup"
echo "  Project ID: $PROJECT_ID"
echo "  Region:     $REGION"
echo " ----------------------------------------------"

# enable APIs from google cloud: Includes Google Run, Cloud SQL, Cloud Build, Secret Manager, Artifact Registry, and Compute Engine
echo "[1/3] Enabling Google Cloud APIs (Please wait, this may take a few minutes)"
gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    cloudbuild.googleapis.com \
    secretmanager.googleapis.com \
    artifactregistry.googleapis.com \
    compute.googleapis.com

echo "APIs enabled successfully."

# creating artifact registry for docker images
echo "[2/3] Creating Docker Artifact Registry..."

# Check if the repository already exists to ensure idempotency without hiding errors
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID" > /dev/null 2>&1; then
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for Insighters Workflow Automation Project"
    echo "Artifact Registry '$REPO_NAME' created."
else
    echo "Artifact Registry '$REPO_NAME' already exists. Skipping creation."
fi


echo "[3/3] Verifying Setup..."
gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" --project="$PROJECT_ID"

echo " ----------------------------------------------"
echo "  Setup Complete"
echo "  You are now ready to deploy using Cloud Build."
echo " ----------------------------------------------"