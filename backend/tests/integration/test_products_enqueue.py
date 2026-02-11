from __future__ import annotations

from app.models import Product
from app.services.database import db


def _product_count(app) -> int:
    with app.app_context():
        return int(Product.query.count())


def _fetch_product(app, product_id: int) -> Product | None:
    with app.app_context():
        return db.session.get(Product, product_id)


def test_post_products_enqueues_operation_without_direct_db_write(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
):
    response = client.post(
        "/products",
        headers=auth_headers,
        json={"nome": "Mouse", "marca": "ACME", "valor": 50},
    )

    assert response.status_code == 202
    body = response.get_json()
    assert body["status"] == "queued"
    assert body["operation"] == "create"
    assert isinstance(body["operation_id"], str)
    assert int(redis_client.llen(queue_name)) == 1
    assert _product_count(app) == 0


def test_post_products_invalid_payload_returns_400_and_does_not_enqueue(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
):
    response = client.post(
        "/products",
        headers=auth_headers,
        json={"nome": "", "marca": "ACME", "valor": -10},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "nome_is_required"}
    assert int(redis_client.llen(queue_name)) == 0
    assert _product_count(app) == 0


def test_put_products_existing_id_enqueues_without_direct_db_write(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
    seed_product,
):
    seeded = seed_product(nome="Mouse antigo", marca="A", valor=10)

    response = client.put(
        f"/products/{seeded['id']}",
        headers=auth_headers,
        json={"nome": "Mouse novo", "marca": "B", "valor": 25.5},
    )

    assert response.status_code == 202
    body = response.get_json()
    assert body["status"] == "queued"
    assert body["operation"] == "update"
    assert body["product_id"] == seeded["id"]
    assert int(redis_client.llen(queue_name)) == 1

    current_product = _fetch_product(app, seeded["id"])
    assert current_product is not None
    assert current_product.nome == "Mouse antigo"
    assert current_product.marca == "A"


def test_put_products_nonexistent_id_returns_404_without_enqueue(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
):
    response = client.put(
        "/products/9999",
        headers=auth_headers,
        json={"nome": "X", "marca": "Y", "valor": 15},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "product_not_found"}
    assert int(redis_client.llen(queue_name)) == 0
    assert _product_count(app) == 0


def test_delete_products_existing_id_enqueues_without_direct_db_delete(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
    seed_product,
):
    seeded = seed_product(nome="Fone", marca="Bose", valor=100)

    response = client.delete(f"/products/{seeded['id']}", headers=auth_headers)

    assert response.status_code == 202
    body = response.get_json()
    assert body["status"] == "queued"
    assert body["operation"] == "delete"
    assert body["product_id"] == seeded["id"]
    assert int(redis_client.llen(queue_name)) == 1
    assert _fetch_product(app, seeded["id"]) is not None


def test_delete_products_nonexistent_id_returns_404_without_enqueue(
    app,
    client,
    auth_headers,
    redis_client,
    queue_name,
):
    response = client.delete("/products/9999", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json() == {"error": "product_not_found"}
    assert int(redis_client.llen(queue_name)) == 0
    assert _product_count(app) == 0
