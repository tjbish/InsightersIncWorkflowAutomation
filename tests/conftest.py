from __future__ import annotations

import datetime
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import pytest
import requests


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT_DIR / ".env"


def _load_dotenv() -> None:
    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        os.environ.setdefault(key, value)


_load_dotenv()


def build_url(base_url: str, path: str) -> str:
    return urljoin(f"{base_url.rstrip('/')}/", path.lstrip("/"))


def _extract_csrf_token(response_text: str) -> str:
    match = re.search(r'name="csrfmiddlewaretoken"\s+value="([^"]+)"', response_text)
    assert match, "Could not find csrfmiddlewaretoken in response HTML."
    return match.group(1)


def get_form_page(session: requests.Session, base_url: str, path: str) -> requests.Response:
    response = session.get(build_url(base_url, path), timeout=30)
    assert response.status_code == 200, f"Expected 200 for GET {path}, got {response.status_code}"
    return response


def post_with_csrf(
    session: requests.Session,
    base_url: str,
    path: str,
    data: dict[str, Any],
    *,
    allow_redirects: bool = True,
    timeout: int = 30,
) -> requests.Response:
    form_page = get_form_page(session, base_url, path)
    csrf_token = _extract_csrf_token(form_page.text)
    payload = {"csrfmiddlewaretoken": csrf_token, **data}
    return session.post(
        build_url(base_url, path),
        data=payload,
        headers={"Referer": build_url(base_url, path)},
        allow_redirects=allow_redirects,
        timeout=timeout,
    )


def login_for_intake_path(session: requests.Session, base_url: str, protected_path: str) -> requests.Response:
    login_id = os.environ.get("INTAKE_LOGIN_ID")
    password = os.environ.get("INTAKE_LOGIN_PASSWORD")
    if not login_id or not password:
        pytest.skip("INTAKE_LOGIN_ID / INTAKE_LOGIN_PASSWORD are required in .env for intake login tests.")

    preflight = session.get(build_url(base_url, protected_path), allow_redirects=False, timeout=30)
    assert preflight.status_code in {302, 303}, f"Expected redirect when requesting {protected_path}, got {preflight.status_code}"

    return post_with_csrf(
        session,
        base_url,
        "/intake-login/",
        {"login_id": login_id, "password": password},
        allow_redirects=False,
        timeout=30,
    )


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.environ.get("BASE_URL", "http://localhost:8000").rstrip("/")


@pytest.fixture()
def session() -> requests.Session:
    client = requests.Session()
    yield client
    client.close()


@pytest.fixture()
def valid_business_data() -> dict[str, Any]:
    return {
        "owner1_name": "Alabama Test School LLC",
        "owner1_ssn": "111-11-1111",
        "owner1_ownership": "60.00",
        "owner2_name": "Generic Test Partner",
        "owner2_ssn": "222-22-2222",
        "owner2_ownership": "40.00",
        "business_name": "Alabama Test School",
        "fin_number": "12-3456789",
        "email": "alabama.business.integration@example.com",
        "address": "100 Generic Avenue",
        "city": "Tuscaloosa",
        "state": "AL",
        "zip_code": "35401",
        "phone_number": "205-555-0100",
        "cell_number": "205-555-0101",
        "fax_number": "205-555-0102",
        "business_type": "service",
        "business_structure": "llc",
        "date_established": "2014-08-15",
        "date_last_return": "2025-03-20",
        "sales_yr1": "150000.00",
        "sales_yr2": "175000.00",
        "sales_yr3": "210000.00",
        "sales_current": "98000.00",
        "accounting_period": "fiscal",
        "fiscal_year_end": "2025-12-31",
        "bank_name": "First Generic Bank",
        "bank_account_type": "checking",
        "bank_account_number": "1234567890",
        "bank_contact_name": "Jordan Banker",
        "bank_contact_phone": "205-555-0103",
        "bank_name2": "Second Generic Bank",
        "bank_account_type2": "savings",
        "bank_account_number2": "0987654321",
        "bank_contact_name2": "Taylor Treasury",
        "bank_contact_phone2": "205-555-0104",
        "accounting_software": "Generic Ledger Pro",
        "has_payroll": "on",
        "num_employees": "12",
        "payroll_id_state": "AL-12345",
        "payroll_id_county": "TUSC-67890",
        "payroll_id_city": "CITY-11223",
        "sales_tax_state": "AL-ST-9988",
        "sales_tax_county": "TUSC-ST-7766",
        "sales_tax_city": "CITY-ST-5544",
    }


@pytest.fixture()
def valid_individual_data() -> dict[str, Any]:
    current_year = datetime.date.today().year
    return {
        "client_status": "existing",
        "tax_year": str(current_year - 1),
        "client_name": "Alex Example",
        "client_dob": "1988-04-12",
        "client_ssn": "333-33-3333",
        "client_occupation": "Teacher",
        "client_dl": "ALX1234567",
        "client_dl_exp": "2028-04-12",
        "client_dl_issued": "2020-04-12",
        "spouse_name": "Jamie Example",
        "spouse_dob": "1989-09-21",
        "spouse_ssn": "444-44-4444",
        "spouse_occupation": "Nurse",
        "spouse_dl": "JME7654321",
        "spouse_dl_exp": "2028-09-21",
        "spouse_dl_issued": "2020-09-21",
        "address": "250 Example Lane",
        "city": "Birmingham",
        "state": "AL",
        "zip_code": "35203",
        "phone_number": "205-555-0200",
        "cell_number": "205-555-0201",
        "email": "alex.individual.integration@example.com",
        "filing_status": "mfj",
        "dep1_name": "Casey Example",
        "dep1_dob": "2015-06-10",
        "dep1_ssn": "555-55-5555",
        "dep1_rel": "Child",
        "dep1_months": "12",
        "dep2_name": "Morgan Example",
        "dep2_dob": "2018-08-22",
        "dep2_ssn": "666-66-6666",
        "dep2_rel": "Child",
        "dep2_months": "12",
        "dep3_name": "Riley Example",
        "dep3_dob": "2021-01-14",
        "dep3_ssn": "777-77-7777",
        "dep3_rel": "Child",
        "dep3_months": "12",
        "income_sources": ["income", "business", "other"],
        "income_other": "Test royalties",
        "expenses": ["education", "other_exp"],
        "expenses_other": "Generic classroom supplies",
        "certification": "on",
        "client_signature": "Alex Example",
        "date_signed": "2026-04-15",
    }
