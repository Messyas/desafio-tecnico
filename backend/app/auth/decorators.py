from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request

from .service import AuthError, decode_access_token


def _unauthorized(reason: str):
    return jsonify({"error": reason}), 401


def require_auth(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        if not authorization.startswith("Bearer "):
            return _unauthorized("missing_token")

        token = authorization.split(" ", 1)[1].strip()
        if not token:
            return _unauthorized("missing_token")

        try:
            payload = decode_access_token(token)
        except AuthError as exc:
            return _unauthorized(str(exc))

        g.current_user_id = int(payload["sub"])
        g.current_user_identifier = str(payload.get("identifier") or "")
        return view_func(*args, **kwargs)

    return wrapped
