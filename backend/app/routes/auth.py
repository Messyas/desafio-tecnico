from __future__ import annotations

from flask import current_app, jsonify, request
from sqlalchemy import func

from . import api_bp
from ..auth.service import create_access_token, verify_password
from ..models import User


@api_bp.route("/auth/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_payload"}), 400

    identifier = payload.get("identifier")
    password = payload.get("password")
    if not isinstance(identifier, str) or not isinstance(password, str):
        return jsonify({"error": "invalid_payload"}), 400

    normalized_identifier = identifier.strip()
    if not normalized_identifier or not password:
        return jsonify({"error": "invalid_payload"}), 400

    identifier_lower = normalized_identifier.lower()
    user = User.query.filter(
        func.lower(User.email) == identifier_lower
    ).one_or_none()
    if user is None:
        user = User.query.filter(
            func.lower(User.name) == identifier_lower
        ).one_or_none()

    if user is None or not verify_password(password, user.password_hash):
        return jsonify({"error": "invalid_credentials"}), 401

    access_token = create_access_token(user_id=user.id, identifier=user.name)
    return (
        jsonify(
            {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(current_app.config["JWT_EXPIRES_SECONDS"]),
            }
        ),
        200,
    )
