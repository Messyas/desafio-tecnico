from __future__ import annotations


def test_login_success_with_username(client, test_user):
    response = client.post(
        "/auth/login",
        json={"identifier": test_user["name"], "password": test_user["password"]},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert isinstance(body["access_token"], str)
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 3600


def test_login_success_with_email(client, test_user):
    response = client.post(
        "/auth/login",
        json={"identifier": test_user["email"], "password": test_user["password"]},
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


def test_products_requires_valid_token(client):
    response = client.get("/products")

    assert response.status_code == 401
    assert response.get_json() == {"error": "missing_token"}
