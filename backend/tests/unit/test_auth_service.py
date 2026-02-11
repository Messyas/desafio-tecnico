from __future__ import annotations

import pytest
from flask import Flask

from app.auth import init_auth
from app.auth.service import AuthError, create_access_token, decode_access_token, hash_password, verify_password


@pytest.fixture
def auth_app():
    flask_app = Flask(__name__)
    flask_app.config["JWT_SECRET_KEY"] = "unit-test-secret"
    flask_app.config["JWT_EXPIRES_SECONDS"] = 120
    init_auth(flask_app)
    return flask_app


def test_create_and_decode_access_token(auth_app):
    with auth_app.app_context():
        token = create_access_token(user_id=7, identifier="alice")
        payload = decode_access_token(token)

    assert payload["sub"] == "7"
    assert payload["identifier"] == "alice"


def test_decode_access_token_rejects_invalid_token(auth_app):
    with auth_app.app_context():
        with pytest.raises(AuthError):
            decode_access_token("not-a-jwt")


def test_hash_password_and_verify_password():
    password_hash = hash_password("my-password")

    assert password_hash != "my-password"
    assert verify_password("my-password", password_hash)
    assert not verify_password("wrong-password", password_hash)
