from __future__ import annotations

from app.auth.service import decode_access_token
from app.models import User
from app.services.database import db


def test_register_success_returns_201_and_token(app, client):
    response = client.post(
        "/auth/register",
        json={
            "name": "new-user",
            "email": "New-User@Example.com",
            "password": "strong-pass",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert isinstance(body["access_token"], str)
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 3600

    with app.app_context():
        payload = decode_access_token(body["access_token"])
        user = db.session.get(User, int(payload["sub"]))
        assert user is not None
        assert user.name == "new-user"
        assert user.email == "new-user@example.com"


def test_register_rejects_invalid_payload(client):
    response = client.post("/auth/register", json={"name": "x"})

    assert response.status_code == 400
    assert response.get_json() == {"error": "invalid_payload"}


def test_register_rejects_short_password(client):
    response = client.post(
        "/auth/register",
        json={"name": "x", "email": "x@example.com", "password": "short"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "password_too_short"}


def test_register_conflict_on_email_case_insensitive_returns_409(client, test_user):
    response = client.post(
        "/auth/register",
        json={
            "name": "another-name",
            "email": str(test_user["email"]).upper(),
            "password": "valid-pass",
        },
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "email_already_exists"}


def test_register_conflict_on_name_case_insensitive_returns_409(client, test_user):
    response = client.post(
        "/auth/register",
        json={
            "name": str(test_user["name"]).upper(),
            "email": "another-email@example.com",
            "password": "valid-pass",
        },
    )

    assert response.status_code == 409
    assert response.get_json() == {"error": "name_already_exists"}


def test_logout_success_with_valid_token_returns_200(client, auth_headers):
    response = client.post("/auth/logout", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"status": "logged_out"}


def test_logout_requires_token_returns_401(client):
    response = client.post("/auth/logout")

    assert response.status_code == 401
    assert response.get_json() == {"error": "missing_token"}
