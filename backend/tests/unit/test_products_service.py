from __future__ import annotations

from decimal import Decimal

import pytest

from app.services.products import validate_product_payload


def test_validate_product_payload_accepts_valid_data():
    payload = validate_product_payload(
        {"nome": " Teclado ", "marca": " Keychron ", "valor": "199.90"}
    )

    assert payload == {
        "nome": "Teclado",
        "marca": "Keychron",
        "valor": Decimal("199.90"),
    }


@pytest.mark.parametrize(
    ("raw_payload", "expected_error"),
    [
        ({}, "nome_must_be_string"),
        ({"nome": "", "marca": "X", "valor": 1}, "nome_is_required"),
        ({"nome": "X", "marca": "", "valor": 1}, "marca_is_required"),
        ({"nome": "X", "marca": "Y", "valor": "abc"}, "valor_must_be_numeric"),
        (
            {"nome": "X", "marca": "Y", "valor": 0},
            "valor_must_be_greater_than_zero",
        ),
    ],
)
def test_validate_product_payload_rejects_invalid_data(raw_payload, expected_error):
    with pytest.raises(ValueError) as exc:
        validate_product_payload(raw_payload)

    assert str(exc.value) == expected_error
