from __future__ import annotations

from flask import Flask
import pytest

from app.routes import api_bp


@pytest.fixture
def app() -> Flask:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(api_bp)
    return app


@pytest.fixture
def client(app: Flask):
    return app.test_client()


def test_openapi_json_returns_spec(client):

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.content_type.startswith("application/json")

    spec = response.get_json()
    assert spec["openapi"] == "3.0.3"
    assert "bearerAuth" in spec["components"]["securitySchemes"]
    assert "/auth/login" in spec["paths"]
    assert "/products" in spec["paths"]
    assert "/products/{product_id}" in spec["paths"]
    assert "/" not in spec["paths"]
    assert "/health" not in spec["paths"]
    assert "/healthz" not in spec["paths"]


def test_openapi_has_security_on_protected_operations(client):

    response = client.get("/openapi.json")
    spec = response.get_json()

    expected_security = [{"bearerAuth": []}]

    assert spec["paths"]["/products"]["get"]["security"] == expected_security
    assert spec["paths"]["/products"]["post"]["security"] == expected_security
    assert spec["paths"]["/products/{product_id}"]["put"]["security"] == expected_security
    assert spec["paths"]["/products/{product_id}"]["delete"]["security"] == expected_security
    assert spec["paths"]["/auth/logout"]["post"]["security"] == expected_security


def test_docs_page_is_public_and_contains_swagger_ui(client):

    response = client.get("/docs")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "SwaggerUIBundle" in body
    assert "openapi.json" in body


def test_removed_health_and_root_routes_return_404(client):

    assert client.get("/").status_code == 404
    assert client.get("/health").status_code == 404
    assert client.get("/healthz").status_code == 404
