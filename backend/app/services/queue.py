from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from flask import current_app
from redis import Redis

from .redis import get_redis_client

ALLOWED_PRODUCT_OPERATIONS = {"create", "update", "delete"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00",
        "Z",
    )


def get_products_queue_name() -> str:
    queue_name = current_app.config.get("PRODUCTS_QUEUE_NAME")
    if not isinstance(queue_name, str) or not queue_name.strip():
        return "queue:products"
    return queue_name


def _decode_message(raw_message: bytes | str) -> dict[str, object]:
    if isinstance(raw_message, bytes):
        raw_message = raw_message.decode("utf-8")

    loaded = json.loads(raw_message)
    if not isinstance(loaded, dict):
        raise ValueError("invalid_queue_message")
    return loaded


def _json_default(value: object):
    if isinstance(value, Decimal):
        return float(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def build_product_operation_message(
    *,
    operation: str,
    requested_by: str,
    product_id: int | None = None,
    payload: dict[str, object] | None = None,
    operation_id: str | None = None,
    requested_at: str | None = None,
) -> dict[str, object]:
    if operation not in ALLOWED_PRODUCT_OPERATIONS:
        raise ValueError("unsupported_operation")

    if operation in {"update", "delete"} and product_id is None:
        raise ValueError("product_id_is_required")

    if operation in {"create", "update"} and payload is None:
        raise ValueError("payload_is_required")

    message = {
        "operation_id": operation_id or str(uuid4()),
        "operation": operation,
        "product_id": product_id,
        "payload": payload,
        "requested_by": requested_by,
        "requested_at": requested_at or utc_now_iso(),
    }
    return message


def enqueue_product_operation(message: dict[str, object], client: Redis | None = None) -> int:
    redis_client = client or get_redis_client()
    queue_name = get_products_queue_name()
    return int(redis_client.lpush(queue_name, json.dumps(message, default=_json_default)))


def pop_product_operation(
    timeout: int = 1,
    client: Redis | None = None,
) -> dict[str, object] | None:
    redis_client = client or get_redis_client()
    queue_name = get_products_queue_name()
    item = redis_client.brpop(queue_name, timeout=max(timeout, 0))
    if item is None:
        return None

    _, raw_message = item
    return _decode_message(raw_message)
