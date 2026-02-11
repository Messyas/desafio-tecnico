from __future__ import annotations

import worker


def _process_next(app) -> bool:
    with app.app_context():
        return worker.process_next_message(timeout=1)


def test_worker_processes_create_after_enqueue(app, client, auth_headers):
    enqueue_response = client.post(
        "/products",
        headers=auth_headers,
        json={"nome": "Mouse", "marca": "ACME", "valor": 80},
    )
    assert enqueue_response.status_code == 202

    before = client.get("/products", headers=auth_headers)
    assert before.status_code == 200
    assert before.get_json() == []

    assert _process_next(app) is True

    after = client.get("/products", headers=auth_headers)
    body = after.get_json()
    assert after.status_code == 200
    assert len(body) == 1
    assert body[0]["nome"] == "Mouse"


def test_worker_processes_update_after_enqueue(app, client, auth_headers, seed_product):
    seeded = seed_product(nome="Notebook", marca="A", valor=3000)

    enqueue_response = client.put(
        f"/products/{seeded['id']}",
        headers=auth_headers,
        json={"nome": "Notebook Pro", "marca": "B", "valor": 3500},
    )
    assert enqueue_response.status_code == 202

    before = client.get("/products", headers=auth_headers).get_json()
    assert before[0]["nome"] == "Notebook"
    assert before[0]["marca"] == "A"

    assert _process_next(app) is True

    after = client.get("/products", headers=auth_headers).get_json()
    assert after[0]["nome"] == "Notebook Pro"
    assert after[0]["marca"] == "B"
    assert after[0]["valor"] == 3500.0


def test_worker_processes_delete_after_enqueue(app, client, auth_headers, seed_product):
    seeded = seed_product(nome="Headset", marca="C", valor=500)

    enqueue_response = client.delete(
        f"/products/{seeded['id']}",
        headers=auth_headers,
    )
    assert enqueue_response.status_code == 202

    before = client.get("/products", headers=auth_headers).get_json()
    assert len(before) == 1

    assert _process_next(app) is True

    after = client.get("/products", headers=auth_headers).get_json()
    assert after == []
