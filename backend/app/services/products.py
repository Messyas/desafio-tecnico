from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

from ..models import Product


def _format_datetime(value: datetime | None) -> str | None:
    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)
    return value.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def serialize_product(product: Product) -> dict[str, object]:
    return {
        "id": product.id,
        "nome": product.nome,
        "marca": product.marca,
        "valor": float(product.valor),
        "created_at": _format_datetime(product.created_at),
        "updated_at": _format_datetime(product.updated_at),
    }


def _normalize_non_empty_str(value: object, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name}_must_be_string")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name}_is_required")
    return normalized


def _normalize_positive_decimal(value: object, field_name: str) -> Decimal:
    try:
        normalized = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError(f"{field_name}_must_be_numeric") from exc

    if normalized <= 0:
        raise ValueError(f"{field_name}_must_be_greater_than_zero")
    return normalized.quantize(Decimal("0.01"))


def validate_product_payload(payload: object) -> dict[str, object]:
    if not isinstance(payload, dict):
        raise ValueError("invalid_payload")

    return {
        "nome": _normalize_non_empty_str(payload.get("nome"), "nome"),
        "marca": _normalize_non_empty_str(payload.get("marca"), "marca"),
        "valor": _normalize_positive_decimal(payload.get("valor"), "valor"),
    }
