from __future__ import annotations

from .conftest import build_url, login_for_intake_path


def test_dashboard_redirects_when_not_authenticated(session, base_url):
    response = session.get(build_url(base_url, "/dashboard/"), allow_redirects=False, timeout=30)
    assert response.status_code in {302, 303}
    assert "/admin-login/" in response.headers.get("Location", "")


def test_intake_login_allows_env_credentials_for_individual_form(session, base_url):
    login_response = login_for_intake_path(session, base_url, "/individual/")
    assert login_response.status_code in {302, 303}
    assert "/individual/" in login_response.headers.get("Location", "")


def test_intake_login_rejects_bad_credentials(session, base_url):
    preflight = session.get(build_url(base_url, "/individual/"), allow_redirects=False, timeout=30)
    assert preflight.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/intake-login/"),
        data={"login_id": "bad-user", "password": "bad-password"},
        timeout=30,
    )
    assert response.status_code == 200
    assert "Invalid login ID or password" in response.text
