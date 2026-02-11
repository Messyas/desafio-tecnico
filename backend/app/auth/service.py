from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from jwt import ExpiredSignatureError, InvalidTokenError
from werkzeug.security import check_password_hash, generate_password_hash

JWT_ALGORITHM = "HS256"


class AuthError(Exception):
    pass


def hash_password(raw_password: str) -> str:
    return generate_password_hash(raw_password)


def verify_password(raw_password: str, password_hash: str) -> bool:
    return check_password_hash(password_hash, raw_password)


def create_access_token(user_id: int, identifier: str) -> str:
    now = datetime.now(timezone.utc)
    expires_in_seconds = int(current_app.config["JWT_EXPIRES_SECONDS"])
    payload = {
        "sub": str(user_id),
        "identifier": identifier,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    secret = current_app.config["JWT_SECRET_KEY"]
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    secret = current_app.config["JWT_SECRET_KEY"]
    try:
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
    except ExpiredSignatureError as exc:
        raise AuthError("expired_token") from exc
    except InvalidTokenError as exc:
        raise AuthError("invalid_token") from exc

    if "sub" not in payload:
        raise AuthError("invalid_token")
    return payload
