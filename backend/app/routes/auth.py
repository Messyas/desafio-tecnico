from __future__ import annotations

from flask import current_app, jsonify, request
from sqlalchemy import or_

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

    identifier = identifier.strip()
    if not identifier or not password:
        return jsonify({"error": "invalid_payload"}), 400

    user = User.query.filter(
        or_(User.name == identifier, User.email == identifier)
    ).first()
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
