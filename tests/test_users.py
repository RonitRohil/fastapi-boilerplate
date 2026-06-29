"""User endpoint tests: /me, list, get, update, create (admin), delete."""

from tests.conftest import VALID_SIGNUP


# ---------------------------------------------------------------------------
# /users/me
# ---------------------------------------------------------------------------


def test_get_me_authenticated(registered_client, auth_headers):
    resp = registered_client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert result["email"] == VALID_SIGNUP["email"]
    assert result["username"] == VALID_SIGNUP["username"]
    assert "hashed_password" not in result


def test_get_me_unauthenticated(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 401


def test_update_me(registered_client, auth_headers):
    csrf = registered_client.cookies.get("csrf_token")
    resp = registered_client.put(
        "/api/v1/users/update/me",
        json={"first_name": "Updated"},
        headers={**auth_headers, "X-CSRF-Token": csrf},
    )
    assert resp.status_code == 200
    assert resp.json()["result"]["first_name"] == "Updated"


def test_update_me_without_csrf_returns_403(registered_client, auth_headers):
    resp = registered_client.put(
        "/api/v1/users/update/me",
        json={"first_name": "Hack"},
        headers=auth_headers,
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /users/get/{user_id}
# ---------------------------------------------------------------------------


def test_get_user_by_id(registered_client, auth_headers):
    me = registered_client.get("/api/v1/users/me", headers=auth_headers).json()[
        "result"
    ]
    resp = registered_client.get(f"/api/v1/users/get/{me['id']}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["result"]["id"] == me["id"]


def test_get_user_not_found(registered_client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = registered_client.get(f"/api/v1/users/get/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /users/get/list
# ---------------------------------------------------------------------------


def test_get_users_list(registered_client, auth_headers):
    resp = registered_client.get("/api/v1/users/get/list", headers=auth_headers)
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert "users" in result
    assert "total" in result
    assert result["total"] >= 1


def test_get_users_list_unauthenticated(client):
    resp = client.get("/api/v1/users/get/list")
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Admin: POST /users/create
# ---------------------------------------------------------------------------


def test_create_user_as_non_admin_returns_403(registered_client, auth_headers):
    resp = registered_client.post(
        "/api/v1/users/create",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass1",
            "role": "user",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403


def test_create_user_invalid_role_returns_422(registered_client, auth_headers):
    resp = registered_client.post(
        "/api/v1/users/create",
        json={
            "username": "hacker",
            "email": "hacker@example.com",
            "password": "HackPass1",
            "role": "superuser",  # not in Literal["user", "admin"]
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /users/delete/{user_id}
# ---------------------------------------------------------------------------


def test_delete_user_as_non_admin_returns_403(registered_client, auth_headers):
    me = registered_client.get("/api/v1/users/me", headers=auth_headers).json()[
        "result"
    ]
    resp = registered_client.delete(
        f"/api/v1/users/delete/{me['id']}",
        headers=auth_headers,
    )
    assert resp.status_code == 403
