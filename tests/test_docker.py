from __future__ import annotations

from .conftest import build_url


def test_app_root_is_reachable(session, base_url):
    response = session.get(build_url(base_url, "/"), timeout=30)
    assert response.status_code == 200


def test_login_pages_load_when_container_is_running(session, base_url):
    intake_login = session.get(build_url(base_url, "/intake-login/"), timeout=30)
    admin_login = session.get(build_url(base_url, "/admin-login/"), timeout=30)

    assert intake_login.status_code == 200
    assert admin_login.status_code == 200
    assert "Login ID" in intake_login.text
    assert "Admin Access" in admin_login.text
