"""Auth endpoint tests: signup, login, refresh, logout, password reset."""

from tests.conftest import VALID_SIGNUP


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------


def test_signup_success(client):
    resp = client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 201
    body = resp.json()
    assert body["success"] == 1
    assert "user" in body["result"]
    assert "access_token" not in body["result"]  # tokens stay in cookies
    assert "refresh_token" not in body["result"]
    # Cookies must be set
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies
    assert "csrf_token" in resp.cookies


def test_signup_duplicate_email(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    resp = client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    assert resp.status_code == 400


def test_signup_duplicate_username(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    payload = {**VALID_SIGNUP, "email": "other@example.com"}
    resp = client.post("/api/v1/auth/signup", json=payload)
    assert resp.status_code == 400


def test_signup_weak_password_too_short(client):
    resp = client.post("/api/v1/auth/signup", json={**VALID_SIGNUP, "password": "Ab1"})
    assert resp.status_code == 422


def test_signup_weak_password_no_uppercase(client):
    resp = client.post(
        "/api/v1/auth/signup", json={**VALID_SIGNUP, "password": "testpass1"}
    )
    assert resp.status_code == 422


def test_signup_weak_password_no_digit(client):
    resp = client.post(
        "/api/v1/auth/signup", json={**VALID_SIGNUP, "password": "TestPassword"}
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------


def test_login_success(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": VALID_SIGNUP["email"],
            "password": VALID_SIGNUP["password"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] == 1
    assert "user" in body["result"]
    assert "access_token" not in body["result"]
    assert "access_token" in resp.cookies


def test_login_wrong_password(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": VALID_SIGNUP["email"],
            "password": "WrongPass9",
        },
    )
    assert resp.status_code == 400
    assert "Invalid" in resp.json()["detail"]


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nobody@example.com",
            "password": "TestPass1",
        },
    )
    assert resp.status_code == 400
    # Same error message — no email enumeration
    assert "Invalid" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------


def test_refresh_returns_new_access_cookie(registered_client):
    resp = registered_client.post("/api/v1/auth/refresh")
    assert resp.status_code == 200
    assert "access_token" in resp.cookies


def test_refresh_without_cookie_returns_401(client):
    resp = client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------


def test_logout_clears_cookies(registered_client):
    csrf = registered_client.cookies.get("csrf_token")
    resp = registered_client.post(
        "/api/v1/auth/logout",
        headers={"X-CSRF-Token": csrf},
    )
    assert resp.status_code == 200
    assert resp.json()["success"] == 1


def test_logout_without_csrf_returns_403(registered_client):
    resp = registered_client.post("/api/v1/auth/logout")
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Forgot / reset password
# ---------------------------------------------------------------------------


def test_forgot_password_unknown_email_same_response(client):
    """Never reveal whether an email is registered."""
    resp = client.post(
        "/api/v1/auth/forgot/password", json={"email": "nobody@example.com"}
    )
    assert resp.status_code == 200
    assert "reset link" in resp.json()["result"]["message"]


def test_forgot_password_known_email_debug_token(client):
    """DEBUG=True (default in tests) returns the token so we can test reset."""
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    resp = client.post(
        "/api/v1/auth/forgot/password", json={"email": VALID_SIGNUP["email"]}
    )
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert "debug_token" in result


def test_reset_password_success(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    forgot = client.post(
        "/api/v1/auth/forgot/password", json={"email": VALID_SIGNUP["email"]}
    )
    token = forgot.json()["result"]["debug_token"]

    resp = client.post(
        "/api/v1/auth/reset/password",
        json={
            "token": token,
            "new_password": "NewPass99",
        },
    )
    assert resp.status_code == 200


def test_reset_password_one_time_use(client):
    """Using the same reset token twice must fail on the second attempt."""
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    forgot = client.post(
        "/api/v1/auth/forgot/password", json={"email": VALID_SIGNUP["email"]}
    )
    token = forgot.json()["result"]["debug_token"]

    client.post(
        "/api/v1/auth/reset/password",
        json={"token": token, "new_password": "NewPass99"},
    )
    second = client.post(
        "/api/v1/auth/reset/password",
        json={"token": token, "new_password": "AnotherPass1"},
    )
    assert second.status_code == 400


def test_reset_password_weak_new_password(client):
    client.post("/api/v1/auth/signup", json=VALID_SIGNUP)
    forgot = client.post(
        "/api/v1/auth/forgot/password", json={"email": VALID_SIGNUP["email"]}
    )
    token = forgot.json()["result"]["debug_token"]

    resp = client.post(
        "/api/v1/auth/reset/password", json={"token": token, "new_password": "weak"}
    )
    assert resp.status_code == 422
