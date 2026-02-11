from __future__ import annotations

from flask import Flask

from app.services import redis as redis_service


def test_configure_redis_builds_operational_and_readiness_clients(monkeypatch):
    calls: list[dict[str, object]] = []
    clients = [object(), object()]

    def fake_build_client(
        redis_url: str,
        *,
        connect_timeout_ms: int,
        socket_timeout_ms: int,
    ) -> object:
        calls.append(
            {
                "redis_url": redis_url,
                "connect_timeout_ms": connect_timeout_ms,
                "socket_timeout_ms": socket_timeout_ms,
            }
        )
        return clients[len(calls) - 1]

    monkeypatch.setattr(redis_service, "_build_redis_client", fake_build_client)

    app = Flask(__name__)
    app.config.update(
        {
            "REDIS_URL": "redis://redis:6379/9",
            "REDIS_REQUIRED": False,
            "REDIS_SOCKET_CONNECT_TIMEOUT_MS": 1500,
            "REDIS_SOCKET_TIMEOUT_MS": 7000,
            "READINESS_REDIS_TIMEOUT_MS": 300,
            "PRODUCTS_QUEUE_NAME": "queue:products:test",
        }
    )

    redis_service.configure_redis(app)

    assert app.extensions["redis_client"] is clients[0]
    assert app.extensions["redis_readiness_client"] is clients[1]
    assert app.config["REDIS_CLIENT"] is clients[0]
    assert app.config["REDIS_READINESS_CLIENT"] is clients[1]
    assert calls == [
        {
            "redis_url": "redis://redis:6379/9",
            "connect_timeout_ms": 1500,
            "socket_timeout_ms": 7000,
        },
        {
            "redis_url": "redis://redis:6379/9",
            "connect_timeout_ms": 300,
            "socket_timeout_ms": 300,
        },
    ]


def test_configure_redis_reads_new_timeout_env_vars(monkeypatch):
    calls: list[dict[str, object]] = []

    def fake_build_client(
        redis_url: str,
        *,
        connect_timeout_ms: int,
        socket_timeout_ms: int,
    ) -> object:
        calls.append(
            {
                "redis_url": redis_url,
                "connect_timeout_ms": connect_timeout_ms,
                "socket_timeout_ms": socket_timeout_ms,
            }
        )
        return object()

    monkeypatch.setattr(redis_service, "_build_redis_client", fake_build_client)
    monkeypatch.setenv("REDIS_URL", "redis://redis:6379/11")
    monkeypatch.setenv("REDIS_REQUIRED", "false")
    monkeypatch.setenv("REDIS_SOCKET_CONNECT_TIMEOUT_MS", "1200")
    monkeypatch.setenv("REDIS_SOCKET_TIMEOUT_MS", "4200")
    monkeypatch.setenv("READINESS_REDIS_TIMEOUT_MS", "250")
    monkeypatch.setenv("PRODUCTS_QUEUE_NAME", "queue:products:test")

    app = Flask(__name__)
    redis_service.configure_redis(app)

    assert app.config["REDIS_SOCKET_CONNECT_TIMEOUT_MS"] == 1200
    assert app.config["REDIS_SOCKET_TIMEOUT_MS"] == 4200
    assert app.config["READINESS_REDIS_TIMEOUT_MS"] == 250
    assert calls == [
        {
            "redis_url": "redis://redis:6379/11",
            "connect_timeout_ms": 1200,
            "socket_timeout_ms": 4200,
        },
        {
            "redis_url": "redis://redis:6379/11",
            "connect_timeout_ms": 250,
            "socket_timeout_ms": 250,
        },
    ]


def test_check_redis_uses_readiness_client(monkeypatch):
    readiness_client = object()
    captured: dict[str, object] = {}

    def fake_ping(client: object) -> dict[str, object]:
        captured["client"] = client
        return {"ok": True, "duration_ms": 1}

    monkeypatch.setattr(redis_service, "_ping_redis", fake_ping)

    app = Flask(__name__)
    app.extensions["redis_readiness_client"] = readiness_client

    with app.app_context():
        result = redis_service.check_redis()

    assert result["ok"] is True
    assert captured["client"] is readiness_client
