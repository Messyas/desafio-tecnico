from __future__ import annotations

import os
from decimal import Decimal

import pytest
from flask_migrate import upgrade
from sqlalchemy import text

from app import create_app
from app.auth.service import create_access_token, hash_password
from app.models import Product, User
from app.services.database import db

DEFAULT_DATABASE_URL = "postgresql+psycopg://postgres:postgres@db:5432/desafio"
DEFAULT_TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL))
DEFAULT_TEST_REDIS_URL = os.getenv("TEST_REDIS_URL", "redis://redis:6379/15")
DEFAULT_TEST_QUEUE_NAME = os.getenv("TEST_PRODUCTS_QUEUE_NAME", "queue:products:test")


def _truncate_tables() -> None:
    db.session.execute(text("TRUNCATE TABLE product RESTART IDENTITY CASCADE"))
    db.session.execute(text('TRUNCATE TABLE "user" RESTART IDENTITY CASCADE'))
    db.session.commit()


@pytest.fixture(scope="session")
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": DEFAULT_TEST_DATABASE_URL,
        "REDIS_URL": DEFAULT_TEST_REDIS_URL,
        "REDIS_REQUIRED": False,
        "PRODUCTS_QUEUE_NAME": DEFAULT_TEST_QUEUE_NAME,
        "JWT_SECRET_KEY": "test-secret-key",
        "JWT_EXPIRES_SECONDS": 3600,
    }
    flask_app = create_app(test_config)
    with flask_app.app_context():
        upgrade(directory="migrations")
    yield flask_app


@pytest.fixture(autouse=True)
def clean_state(app):
    with app.app_context():
        _truncate_tables()
        app.extensions["redis_client"].flushdb()
    yield
    with app.app_context():
        _truncate_tables()
        app.extensions["redis_client"].flushdb()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def queue_name(app):
    with app.app_context():
        return str(app.config["PRODUCTS_QUEUE_NAME"])


@pytest.fixture
def redis_client(app):
    with app.app_context():
        return app.extensions["redis_client"]


@pytest.fixture
def test_user(app):
    password = "strong-password"
    with app.app_context():
        user = User(
            name="test-user",
            email="test-user@example.com",
            password_hash=hash_password(password),
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "password": password,
        }


@pytest.fixture
def auth_headers(app, test_user):
    with app.app_context():
        access_token = create_access_token(
            user_id=int(test_user["id"]),
            identifier=str(test_user["name"]),
        )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def seed_product(app):
    def _seed(*, nome: str = "Mouse", marca: str = "Logi", valor: Decimal = Decimal("99.90")):
        with app.app_context():
            product = Product(nome=nome, marca=marca, valor=valor)
            db.session.add(product)
            db.session.commit()
            db.session.refresh(product)
            return {
                "id": product.id,
                "nome": product.nome,
                "marca": product.marca,
                "valor": float(product.valor),
            }

    return _seed
