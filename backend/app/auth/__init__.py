import os

from flask import Flask

DEFAULT_JWT_EXPIRES_SECONDS = 3600


def _read_positive_int(value: str | None, default: int) -> int:
    if value is None:
        return default
    try:
        parsed = int(value)
        if parsed <= 0:
            return default
        return parsed
    except ValueError:
        return default


def init_auth(app: Flask) -> None:
    secret = app.config.get("JWT_SECRET_KEY") or os.getenv(
        "JWT_SECRET_KEY",
        "change-me-in-production",
    )
    expires_in_seconds = _read_positive_int(
        str(app.config.get("JWT_EXPIRES_SECONDS"))
        if app.config.get("JWT_EXPIRES_SECONDS") is not None
        else os.getenv("JWT_EXPIRES_SECONDS"),
        DEFAULT_JWT_EXPIRES_SECONDS,
    )

    app.config["JWT_SECRET_KEY"] = secret
    app.config["JWT_EXPIRES_SECONDS"] = expires_in_seconds
