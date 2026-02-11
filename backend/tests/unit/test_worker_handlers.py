from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import Mock

from redis.exceptions import TimeoutError as RedisTimeoutError
import worker


@dataclass
class FakeProduct:
    nome: str
    marca: str
    valor: object
    id: int | None = None


class FakeSession:
    def __init__(self):
        self.storage: dict[int, FakeProduct] = {}
        self._next_id = 1
        self.commits = 0
        self.rollbacks = 0

    def add(self, product: FakeProduct):
        if product.id is None:
            product.id = self._next_id
            self._next_id += 1
        self.storage[product.id] = product

    def get(self, _model, product_id: int):
        return self.storage.get(product_id)

    def delete(self, product: FakeProduct):
        if product.id in self.storage:
            del self.storage[product.id]

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1


def _install_fakes(monkeypatch):
    fake_session = FakeSession()
    monkeypatch.setattr(worker, "db", SimpleNamespace(session=fake_session))
    monkeypatch.setattr(worker, "Product", FakeProduct)
    return fake_session


def test_process_message_create(monkeypatch):
    fake_session = _install_fakes(monkeypatch)

    processed = worker.process_message(
        {
            "operation_id": "op-1",
            "operation": "create",
            "payload": {"nome": "Mouse", "marca": "ACME", "valor": 10},
        }
    )

    assert processed is True
    assert fake_session.commits == 1
    assert len(fake_session.storage) == 1
    created = next(iter(fake_session.storage.values()))
    assert created.nome == "Mouse"


def test_process_message_update(monkeypatch):
    fake_session = _install_fakes(monkeypatch)
    existing = FakeProduct(id=10, nome="Velho", marca="X", valor=1)
    fake_session.storage[10] = existing

    processed = worker.process_message(
        {
            "operation_id": "op-2",
            "operation": "update",
            "product_id": 10,
            "payload": {"nome": "Novo", "marca": "Y", "valor": 2.5},
        }
    )

    assert processed is True
    assert fake_session.commits == 1
    assert fake_session.storage[10].nome == "Novo"
    assert fake_session.storage[10].marca == "Y"


def test_process_message_delete(monkeypatch):
    fake_session = _install_fakes(monkeypatch)
    existing = FakeProduct(id=11, nome="Teclado", marca="ACME", valor=50)
    fake_session.storage[11] = existing

    processed = worker.process_message(
        {
            "operation_id": "op-3",
            "operation": "delete",
            "product_id": 11,
        }
    )

    assert processed is True
    assert fake_session.commits == 1
    assert 11 not in fake_session.storage


def test_process_message_invalid_message_rolls_back(monkeypatch):
    fake_session = _install_fakes(monkeypatch)

    processed = worker.process_message({"operation_id": "op-4", "operation": "unknown"})

    assert processed is False
    assert fake_session.commits == 0
    assert fake_session.rollbacks == 1


def test_process_next_message_handles_redis_timeout_without_exception_log(monkeypatch):
    logger = Mock()

    def raise_timeout(timeout):
        raise RedisTimeoutError("Timeout reading from socket")

    monkeypatch.setattr(worker, "pop_product_operation", raise_timeout)

    processed = worker.process_next_message(timeout=2, logger=logger)

    assert processed is False
    logger.exception.assert_not_called()
    logger.debug.assert_called_once_with("Worker queue poll timed out timeout=%s", 2)


def test_process_next_message_logs_unexpected_queue_errors(monkeypatch):
    logger = Mock()

    def raise_error(timeout):
        raise RuntimeError("redis_unavailable")

    monkeypatch.setattr(worker, "pop_product_operation", raise_error)

    processed = worker.process_next_message(timeout=2, logger=logger)

    assert processed is False
    logger.debug.assert_not_called()
    logger.exception.assert_called_once()
