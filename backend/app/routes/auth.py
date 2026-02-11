from __future__ import annotations

from flask import current_app, jsonify, request
from sqlalchemy import func

from . import api_bp
from ..auth.decorators import require_auth
from ..auth.service import create_access_token, hash_password, verify_password
from ..services.database import db
from ..models import User

MIN_PASSWORD_LENGTH = 8


def _build_auth_response(user: User, status_code: int):
    access_token = create_access_token(user_id=user.id, identifier=user.name)
    return (
        jsonify(
            {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(current_app.config["JWT_EXPIRES_SECONDS"]),
            }
        ),
        status_code,
    )


@api_bp.route("/auth/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "invalid_payload"}), 400

    name = payload.get("name")
    email = payload.get("email")
    password = payload.get("password")
    if not isinstance(name, str) or not isinstance(email, str) or not isinstance(
        password,
        str,
    ):
        return jsonify({"error": "invalid_payload"}), 400

    normalized_name = name.strip()
    normalized_email = email.strip().lower()
    if not normalized_name or not normalized_email:
        return jsonify({"error": "invalid_payload"}), 400

    if len(password) < MIN_PASSWORD_LENGTH:
        return jsonify({"error": "password_too_short"}), 400

    existing_email = User.query.filter(
        func.lower(User.email) == normalized_email
    ).one_or_none()
    if existing_email is not None:
        return jsonify({"error": "email_already_exists"}), 409

    existing_name = User.query.filter(
        func.lower(User.name) == normalized_name.lower()
    ).one_or_none()
    if existing_name is not None:
        return jsonify({"error": "name_already_exists"}), 409

    user = User(
        name=normalized_name,
        email=normalized_email,
        password_hash=hash_password(password),
    )
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)

    return _build_auth_response(user, 201)


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

    return _build_auth_response(user, 200)


@api_bp.route("/auth/logout", methods=["POST"])
@require_auth
def logout():
    return jsonify({"status": "logged_out"}), 200
