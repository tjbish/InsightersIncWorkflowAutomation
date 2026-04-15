from __future__ import annotations

from .conftest import build_url, login_for_intake_path


def test_individual_form_accepts_valid_fake_submission(session, base_url, valid_individual_data):
    login_response = login_for_intake_path(session, base_url, "/individual/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/individual/"),
        data=valid_individual_data,
        allow_redirects=True,
        timeout=60,
    )
    assert response.status_code == 200
    assert "This field is required" not in response.text
    assert "Personal Form Validation Errors" not in response.text


def test_business_form_accepts_valid_fake_submission(session, base_url, valid_business_data):
    login_response = login_for_intake_path(session, base_url, "/business/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/business/"),
        data=valid_business_data,
        allow_redirects=True,
        timeout=60,
    )
    assert response.status_code == 200
    assert "This field is required" not in response.text
    assert "Business Form Validation Errors" not in response.text


def test_empty_individual_form_is_rejected(session, base_url):
    login_response = login_for_intake_path(session, base_url, "/individual/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/individual/"),
        data={},
        timeout=30,
    )
    assert response.status_code == 200
    assert "This field is required" in response.text


def test_empty_business_form_is_rejected(session, base_url):
    login_response = login_for_intake_path(session, base_url, "/business/")
    assert login_response.status_code in {302, 303}

    response = session.post(
        build_url(base_url, "/business/"),
        data={},
        timeout=30,
    )
    assert response.status_code == 200
    assert "This field is required" in response.text
