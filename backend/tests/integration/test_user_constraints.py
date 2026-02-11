from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from app.auth.service import hash_password
from app.models import User
from app.services.database import db


def test_user_name_must_be_unique_case_insensitive(app):
    with app.app_context():
        first = User(
            name="UniqueName",
            email="first@example.com",
            password_hash=hash_password("password-1"),
        )
        second = User(
            name="uniquename",
            email="second@example.com",
            password_hash=hash_password("password-2"),
        )
        db.session.add(first)
        db.session.commit()

        db.session.add(second)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_user_email_must_be_unique_case_insensitive(app):
    with app.app_context():
        first = User(
            name="user-one",
            email="UniqueEmail@example.com",
            password_hash=hash_password("password-1"),
        )
        second = User(
            name="user-two",
            email="uniqueemail@example.com",
            password_hash=hash_password("password-2"),
        )
        db.session.add(first)
        db.session.commit()

        db.session.add(second)
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
