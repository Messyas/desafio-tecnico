from __future__ import annotations

from flask import g, jsonify, request

from . import api_bp
from ..auth.decorators import require_auth
from ..models import Product
from ..services.database import db
from ..services.products import serialize_product, validate_product_payload
from ..services.queue import build_product_operation_message, enqueue_product_operation


def _bad_request(error: str):
    return jsonify({"error": error}), 400


def _not_found():
    return jsonify({"error": "product_not_found"}), 404


def _queued_response(operation: str, operation_id: str, product_id: int | None = None):
    response = {
        "status": "queued",
        "operation": operation,
        "operation_id": operation_id,
    }
    if product_id is not None:
        response["product_id"] = product_id
    return jsonify(response), 202


def _parse_offset(raw_value: str | None) -> int:
    if raw_value is None:
        return 0

    try:
        parsed = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("offset_must_be_non_negative_integer") from exc

    if parsed < 0:
        raise ValueError("offset_must_be_non_negative_integer")
    return parsed


def _parse_limit(raw_value: str | None) -> int | None:
    if raw_value is None:
        return None

    try:
        parsed = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ValueError("limit_must_be_positive_integer") from exc

    if parsed <= 0:
        raise ValueError("limit_must_be_positive_integer")
    return parsed


@api_bp.route("/products", methods=["GET"])
@require_auth
def list_products():
    try:
        offset = _parse_offset(request.args.get("offset"))
        limit = _parse_limit(request.args.get("limit"))
    except ValueError as exc:
        return _bad_request(str(exc))

    base_query = Product.query.order_by(Product.id.asc())
    total_count = int(base_query.count())

    paginated_query = base_query.offset(offset)
    if limit is not None:
        paginated_query = paginated_query.limit(limit)

    products = paginated_query.all()
    response = jsonify([serialize_product(product) for product in products])
    response.headers["X-Total-Count"] = str(total_count)
    response.headers["X-Offset"] = str(offset)
    if limit is not None:
        response.headers["X-Limit"] = str(limit)
    return response, 200


@api_bp.route("/products", methods=["POST"])
@require_auth
def create_product():
    payload = request.get_json(silent=True)
    try:
        normalized_payload = validate_product_payload(payload)
    except ValueError as exc:
        return _bad_request(str(exc))

    message = build_product_operation_message(
        operation="create",
        payload=normalized_payload,
        requested_by=g.current_user_identifier,
    )
    enqueue_product_operation(message)
    return _queued_response("create", str(message["operation_id"]))


@api_bp.route("/products/<int:product_id>", methods=["PUT"])
@require_auth
def update_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return _not_found()

    payload = request.get_json(silent=True)
    try:
        normalized_payload = validate_product_payload(payload)
    except ValueError as exc:
        return _bad_request(str(exc))

    message = build_product_operation_message(
        operation="update",
        product_id=product.id,
        payload=normalized_payload,
        requested_by=g.current_user_identifier,
    )
    enqueue_product_operation(message)
    return _queued_response("update", str(message["operation_id"]), product.id)


@api_bp.route("/products/<int:product_id>", methods=["DELETE"])
@require_auth
def delete_product(product_id: int):
    product = db.session.get(Product, product_id)
    if product is None:
        return _not_found()

    message = build_product_operation_message(
        operation="delete",
        product_id=product.id,
        requested_by=g.current_user_identifier,
    )
    enqueue_product_operation(message)
    return _queued_response("delete", str(message["operation_id"]), product.id)
