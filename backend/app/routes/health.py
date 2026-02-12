from datetime import datetime, timezone

from . import api_bp
from ..services.database import check_database
from ..services.redis import check_redis


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def _sanitize_error(error: object) -> str:
    message = str(error or "").lower()
    if "timeout" in message:
        return "timeout"
    if "connection" in message or "refused" in message:
        return "connection_failed"
    if message in {"timeout", "connection_failed", "unknown_error"}:
        return message
    return "unknown_error"


def _sanitize_check_result(result: dict[str, object]) -> dict[str, object]:
    check = {
        "ok": bool(result.get("ok", False)),
        "duration_ms": int(result.get("duration_ms", 0)),
    }
    if not check["ok"]:
        check["error"] = _sanitize_error(result.get("error"))
    return check


@api_bp.route("/ready")
def ready():
    database_check = _sanitize_check_result(check_database())
    redis_check = _sanitize_check_result(check_redis())

    ready_to_serve = database_check["ok"] and redis_check["ok"]
    status = "ready" if ready_to_serve else "not_ready"
    status_code = 200 if ready_to_serve else 503

    payload = {
        "status": status,
        "service": "api",
        "checks": {
            "database": database_check,
            "redis": redis_check,
        },
        "time": _utc_now(),
    }
    return payload, status_code
