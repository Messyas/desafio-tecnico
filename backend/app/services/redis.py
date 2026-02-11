import os
from time import perf_counter

from flask import Flask, current_app
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import RedisError
from redis.exceptions import TimeoutError as RedisTimeoutError

DEFAULT_REDIS_URL = "redis://redis:6379/0"
DEFAULT_READINESS_REDIS_TIMEOUT_MS = 250


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    return normalized in {"1", "true", "yes", "on"}


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


def _sanitize_redis_error(exc: Exception) -> str:
    message = str(exc).lower()
    if "timeout" in message:
        return "timeout"

    if isinstance(exc, (RedisConnectionError, RedisError)):
        return "connection_failed"

    if "connection" in message or "refused" in message:
        return "connection_failed"

    return "unknown_error"


def _build_redis_client(redis_url: str, timeout_ms: int) -> Redis:
    timeout_seconds = timeout_ms / 1000
    return Redis.from_url(
        redis_url,
        socket_connect_timeout=timeout_seconds,
        socket_timeout=timeout_seconds,
        decode_responses=False,
    )


def _ping_redis(client: Redis) -> dict[str, object]:
    started = perf_counter()
    try:
        client.ping()
        duration_ms = int((perf_counter() - started) * 1000)
        return {"ok": True, "duration_ms": duration_ms}
    except Exception as exc:
        duration_ms = int((perf_counter() - started) * 1000)
        return {
            "ok": False,
            "duration_ms": duration_ms,
            "error": _sanitize_redis_error(exc),
        }


def configure_redis(app: Flask) -> None:
    redis_url = os.getenv("REDIS_URL", DEFAULT_REDIS_URL)
    redis_required = _parse_bool(os.getenv("REDIS_REQUIRED"), default=False)
    readiness_redis_timeout_ms = _read_positive_int(
        os.getenv("READINESS_REDIS_TIMEOUT_MS"),
        DEFAULT_READINESS_REDIS_TIMEOUT_MS,
    )

    app.config["REDIS_URL"] = redis_url
    app.config["REDIS_REQUIRED"] = redis_required
    app.config["READINESS_REDIS_TIMEOUT_MS"] = readiness_redis_timeout_ms

    client = _build_redis_client(redis_url, readiness_redis_timeout_ms)
    app.extensions["redis_client"] = client

    if redis_required:
        result = _ping_redis(client)
        if not result["ok"]:
            raise RuntimeError(
                "Redis is required but unavailable during startup."
            )


def get_redis_client() -> Redis:
    client = current_app.extensions.get("redis_client")
    if client is None:
        raise RuntimeError("Redis client is not configured for this application.")
    return client


def check_redis() -> dict[str, object]:
    return _ping_redis(get_redis_client())
