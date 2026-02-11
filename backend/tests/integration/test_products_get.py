from __future__ import annotations

from decimal import Decimal

from app.models import Product
from app.services.database import db


def test_get_products_returns_empty_list(client, auth_headers):
    response = client.get("/products", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_get_products_returns_expected_fields(app, client, auth_headers):
    with app.app_context():
        product = Product(nome="Monitor", marca="Dell", valor=Decimal("999.90"))
        db.session.add(product)
        db.session.commit()

    response = client.get("/products", headers=auth_headers)

    assert response.status_code == 200
    body = response.get_json()
    assert len(body) == 1
    item = body[0]
    assert set(item) == {
        "id",
        "nome",
        "marca",
        "valor",
        "created_at",
        "updated_at",
    }
    assert item["nome"] == "Monitor"
    assert item["marca"] == "Dell"
    assert item["valor"] == 999.9
    assert isinstance(item["created_at"], str)
    assert isinstance(item["updated_at"], str)
