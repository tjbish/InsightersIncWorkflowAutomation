from __future__ import annotations

import os
from urllib.parse import urlparse

import psycopg2
import pytest

from .conftest import build_url, login_for_intake_path


def _database_connection():
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is required for database integration tests.")

    parsed = urlparse(database_url)
    return psycopg2.connect(
        dbname=(parsed.path or "").lstrip("/"),
        user=parsed.username,
        password=parsed.password,
        host=parsed.hostname,
        port=parsed.port,
    )


def test_business_submission_persists_and_does_not_echo_sensitive_values(session, base_url, valid_business_data):
    login_response = login_for_intake_path(session, base_url, "/business/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/business/"),
        data=valid_business_data,
        allow_redirects=True,
        timeout=60,
    )
    assert response.status_code == 200
    assert valid_business_data["owner1_ssn"] not in response.text
    assert valid_business_data["bank_account_number"] not in response.text

    conn = _database_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT email, bank_account_type, business_name
                FROM core_businessintakesubmission
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (valid_business_data["email"],),
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row[0] == valid_business_data["email"]
    assert row[1] == valid_business_data["bank_account_type"]
    assert row[2] == valid_business_data["business_name"]


def test_individual_submission_persists_and_does_not_echo_sensitive_values(session, base_url, valid_individual_data):
    login_response = login_for_intake_path(session, base_url, "/individual/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/individual/"),
        data=valid_individual_data,
        allow_redirects=True,
        timeout=60,
    )
    assert response.status_code == 200
    assert valid_individual_data["client_ssn"] not in response.text
    assert valid_individual_data["spouse_ssn"] not in response.text

    conn = _database_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT email, client_name, filing_status
                FROM core_personalintakesubmission
                WHERE email = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (valid_individual_data["email"],),
            )
            row = cursor.fetchone()
    finally:
        conn.close()

    assert row is not None
    assert row[0] == valid_individual_data["email"]
    assert row[1] == valid_individual_data["client_name"]
    assert row[2] == valid_individual_data["filing_status"]
