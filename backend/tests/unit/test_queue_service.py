from __future__ import annotations

import json
from decimal import Decimal

import pytest
from flask import Flask

from app.services.queue import build_product_operation_message, enqueue_product_operation


def test_build_product_operation_message_includes_required_fields():
    message = build_product_operation_message(
        operation="create",
        requested_by="test-user",
        payload={"nome": "Mouse", "marca": "ACME", "valor": 12.5},
        operation_id="op-123",
        requested_at="2026-02-11T12:00:00Z",
    )

    assert message == {
        "operation_id": "op-123",
        "operation": "create",
        "product_id": None,
        "payload": {"nome": "Mouse", "marca": "ACME", "valor": 12.5},
        "requested_by": "test-user",
        "requested_at": "2026-02-11T12:00:00Z",
    }


def test_build_product_operation_message_requires_product_id_for_delete():
    with pytest.raises(ValueError) as exc:
        build_product_operation_message(operation="delete", requested_by="test-user")

    assert str(exc.value) == "product_id_is_required"


def test_build_product_operation_message_requires_supported_operation():
    with pytest.raises(ValueError) as exc:
        build_product_operation_message(
            operation="upsert",
            requested_by="test-user",
            payload={"nome": "x", "marca": "y", "valor": 1},
        )

    assert str(exc.value) == "unsupported_operation"


def test_enqueue_product_operation_serializes_decimal_payload():
    class FakeRedis:
        def __init__(self):
            self.value = ""

        def lpush(self, _queue_name, value):
            self.value = value
            return 1

    app = Flask(__name__)
    app.config["PRODUCTS_QUEUE_NAME"] = "queue:products:test"
    fake_redis = FakeRedis()

    with app.app_context():
        message = build_product_operation_message(
            operation="create",
            requested_by="test-user",
            payload={"nome": "Mouse", "marca": "ACME", "valor": Decimal("12.50")},
            operation_id="op-1",
            requested_at="2026-02-11T12:00:00Z",
        )
        enqueue_product_operation(message, client=fake_redis)

    parsed = json.loads(fake_redis.value)
    assert parsed["payload"]["valor"] == 12.5
