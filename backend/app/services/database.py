import math
import os
from time import perf_counter

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()
migrate = Migrate()

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@db:5432/desafio"
DEFAULT_READINESS_DB_TIMEOUT_MS = 1000


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


def _sanitize_database_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "timeout" in message:
        return "timeout"

    connection_tokens = (
        "connection refused",
        "could not connect",
        "name or service not known",
        "temporary failure",
        "network is unreachable",
        "connection reset",
        "connection aborted",
    )
    if any(token in message for token in connection_tokens):
        return "connection_failed"

    return "unknown_error"


def _build_engine_options(database_url: str, readiness_db_timeout_ms: int):
    engine_options = {"pool_pre_ping": True}

    connect_args = {}
    if database_url.startswith("postgresql"):
        engine_options.update(
            {
                "pool_size": 3,
                "max_overflow": 2,
                "pool_timeout": 30,
                "pool_recycle": 1800,
            }
        )
        connect_timeout_seconds = max(1, math.ceil(readiness_db_timeout_ms / 1000))
        connect_args.setdefault("connect_timeout", connect_timeout_seconds)

    if connect_args:
        engine_options["connect_args"] = connect_args

    return engine_options


def configure_database(app: Flask) -> None:
    database_url = app.config.get("SQLALCHEMY_DATABASE_URI") or os.getenv(
        "DATABASE_URL",
        DEFAULT_DATABASE_URL,
    )
    readiness_db_timeout_ms = _read_positive_int(
        str(app.config.get("READINESS_DB_TIMEOUT_MS"))
        if app.config.get("READINESS_DB_TIMEOUT_MS") is not None
        else os.getenv("READINESS_DB_TIMEOUT_MS"),
        DEFAULT_READINESS_DB_TIMEOUT_MS,
    )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["READINESS_DB_TIMEOUT_MS"] = readiness_db_timeout_ms
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = _build_engine_options(
        database_url,
        readiness_db_timeout_ms,
    )


def check_database() -> dict[str, object]:
    started = perf_counter()
    try:
        with db.engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        duration_ms = int((perf_counter() - started) * 1000)
        return {"ok": True, "duration_ms": duration_ms}
    except Exception as exc:
        duration_ms = int((perf_counter() - started) * 1000)
        return {
            "ok": False,
            "duration_ms": duration_ms,
            "error": _sanitize_database_error(exc),
        }
