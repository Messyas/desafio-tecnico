from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/products", None),
        ("POST", "/products", {"nome": "Mouse", "marca": "ACME", "valor": 10}),
        ("PUT", "/products/1", {"nome": "Mouse", "marca": "ACME", "valor": 10}),
        ("DELETE", "/products/1", None),
    ],
)
def test_products_crud_requires_token(client, method: str, path: str, payload: dict | None):
    response = client.open(path, method=method, json=payload)

    assert response.status_code == 401
    assert response.get_json() == {"error": "missing_token"}


@pytest.mark.parametrize(
    ("method", "path", "payload"),
    [
        ("GET", "/products", None),
        ("POST", "/products", {"nome": "Mouse", "marca": "ACME", "valor": 10}),
        ("PUT", "/products/1", {"nome": "Mouse", "marca": "ACME", "valor": 10}),
        ("DELETE", "/products/1", None),
    ],
)
def test_products_crud_rejects_invalid_token(
    client,
    method: str,
    path: str,
    payload: dict | None,
):
    response = client.open(
        path,
        method=method,
        headers={"Authorization": "Bearer invalid-token"},
        json=payload,
    )

    assert response.status_code == 401
    assert response.get_json() == {"error": "invalid_token"}
