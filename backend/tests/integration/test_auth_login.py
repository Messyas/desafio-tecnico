from __future__ import annotations

from app.auth.service import decode_access_token, hash_password
from app.models import User
from app.services.database import db


def test_login_success_with_username(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "identifier": str(test_user["name"]).upper(),
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body["access_token"], str)
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 3600


def test_login_success_with_email(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "identifier": str(test_user["email"]).upper(),
            "password": test_user["password"],
        },
    )

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body["access_token"], str)


def test_login_invalid_credentials(client, test_user):
    response = client.post(
        "/auth/login",
        json={"identifier": test_user["name"], "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid_credentials"}


def test_login_prioritizes_email_when_identifier_matches_another_username(
    app,
    client,
    test_user,
):
    with app.app_context():
        conflicting_username_user = User(
            name=str(test_user["email"]).upper(),
            email="other-user@example.com",
            password_hash=hash_password("other-password"),
        )
        db.session.add(conflicting_username_user)
        db.session.commit()

    response = client.post(
        "/auth/login",
        json={"identifier": test_user["email"], "password": test_user["password"]},
    )

    assert response.status_code == 200
    token = response.get_json()["access_token"]
    with app.app_context():
        payload = decode_access_token(token)
    assert int(payload["sub"]) == int(test_user["id"])


def test_products_requires_valid_token(client):
    response = client.get("/products")

    assert response.status_code == 401
    assert response.get_json() == {"error": "missing_token"}
