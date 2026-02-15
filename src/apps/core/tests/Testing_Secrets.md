# How to Test Google Secret Manager Locally

This guide explains how to verify that your application is correctly fetching secrets (like API keys and Database URLs) directly from Google Cloud Platform, without deploying to the cloud.

---

## Step 1: Prepare Your Environment

Since our Docker container doesn't have your personal Google Login, you must run this test **natively** on your laptop.

1.  **Open a terminal** in your project root.
2.  **Create/Activate a Virtual Environment** (if you haven't already):
    * **Mac/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * **Windows:**
        ```bash
        python -m venv venv
        venv\Scripts\activate
        ```
3.  **Install Production Requirements**:
    ```bash
    pip install -r requirements.txt
    ```

---

## Step 2: Authenticate with Google

This command opens a browser and creates a temporary session token on your computer. It does **not** download a permanent key file to your project folder.

1.  Run the auth command:
    ```bash
    gcloud auth application-default login
    ```
2.  Log in with the Google Account that owns the GCP Project.

---

## Step 3: Configure the Test Session

You need to tell the system which Google Cloud Project to look at.

* **Mac/Linux:**
    ```bash
    export GOOGLE_CLOUD_PROJECT=your-project-id-here
    ```

* **Windows (PowerShell):**
    ```powershell
    $env:GOOGLE_CLOUD_PROJECT="your-project-id-here"
    ```

---

## Step 4: Run the Connection Test

We will open the Django Shell using **Production Settings**. This forces the app to try and connect to Google Secret Manager immediately.

1.  **Start the Shell:**
    ```bash
    python3 manage.py shell --settings=src.config.settings.production
    ```

2.  **Run this Python Code (Inside the Shell):**
    ```python
    from django.conf import settings
    from src.config.settings.production import get_secret

    # Test 1: Check if the Secret Key loaded
    # If this prints a value, it found it (either from Google OR your local .env)
    print(f"1. Current SECRET_KEY: {settings.SECRET_KEY[:5]}...")

    # Test 2: Verify it is coming from Google
    # Run this to see the raw fetch attempt (returns None if failed)
    # Replace 'DJANGO_SECRET_KEY' with the actual name of a secret in your GCP Console if different
    raw_val = get_secret('DJANGO_SECRET_KEY')
    
    if raw_val:
        print(f"2. SUCCESS: Successfully fetched secret from Google Cloud!")
    else:
        print(f"2. FAILURE: Could not fetch from Google Cloud. Check permissions.")
    ```