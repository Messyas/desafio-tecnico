import logging
import time

from redis.exceptions import TimeoutError as RedisTimeoutError

from app import create_app
from app.models import Product
from app.services.database import check_database
from app.services.database import db
from app.services.products import validate_product_payload
from app.services.queue import pop_product_operation
from app.services.redis import check_redis

LOGGER = logging.getLogger("worker")
LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
DEFAULT_POLL_TIMEOUT_SECONDS = 2
IDLE_SLEEP_SECONDS = 1


def _to_int(value: object, field_name: str) -> int:
    try:
        parsed = int(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"{field_name}_must_be_int") from exc
    return parsed


def _handle_create(message: dict[str, object]) -> int:
    payload = validate_product_payload(message.get("payload"))
    product = Product(
        nome=str(payload["nome"]),
        marca=str(payload["marca"]),
        valor=payload["valor"],
    )
    db.session.add(product)
    db.session.flush()
    if product.id is None:
        raise ValueError("product_id_not_generated")
    return int(product.id)


def _handle_update(message: dict[str, object]) -> int:
    product_id = _to_int(message.get("product_id"), "product_id")
    payload = validate_product_payload(message.get("payload"))

    product = db.session.get(Product, product_id)
    if product is None:
        raise ValueError("product_not_found")

    product.nome = str(payload["nome"])
    product.marca = str(payload["marca"])
    product.valor = payload["valor"]
    db.session.add(product)
    return int(product.id)


def _handle_delete(message: dict[str, object]) -> int:
    product_id = _to_int(message.get("product_id"), "product_id")
    product = db.session.get(Product, product_id)
    if product is None:
        raise ValueError("product_not_found")

    db.session.delete(product)
    return product_id


def process_message(message: dict[str, object], logger: logging.Logger | None = None) -> bool:
    active_logger = logger or LOGGER
    operation = str(message.get("operation") or "")
    operation_id = str(message.get("operation_id") or "")
    product_id: int | None
    raw_product_id = message.get("product_id")
    try:
        product_id = int(raw_product_id) if raw_product_id is not None else None
    except (TypeError, ValueError):
        product_id = None

    if not operation_id:
        active_logger.error("Worker skipped message missing operation_id")
        return False

    try:
        if operation == "create":
            product_id = _handle_create(message)
        elif operation == "update":
            product_id = _handle_update(message)
        elif operation == "delete":
            product_id = _handle_delete(message)
        else:
            raise ValueError("unsupported_operation")

        db.session.commit()
        active_logger.info(
            "Worker processed operation=%s operation_id=%s product_id=%s status=success",
            operation,
            operation_id,
            product_id,
        )
        return True
    except Exception as exc:
        db.session.rollback()
        active_logger.exception(
            "Worker failed operation=%s operation_id=%s product_id=%s status=error error=%s",
            operation,
            operation_id,
            product_id,
            exc,
        )
        return False


def process_next_message(
    timeout: int = DEFAULT_POLL_TIMEOUT_SECONDS,
    logger: logging.Logger | None = None,
) -> bool:
    active_logger = logger or LOGGER
    try:
        message = pop_product_operation(timeout=timeout)
    except RedisTimeoutError:
        active_logger.debug("Worker queue poll timed out timeout=%s", timeout)
        return False
    except Exception as exc:
        active_logger.exception("Worker could not read from queue error=%s", exc)
        return False

    if message is None:
        return False
    return process_message(message, logger=active_logger)


def run_forever(
    *,
    poll_timeout: int = DEFAULT_POLL_TIMEOUT_SECONDS,
    idle_sleep_seconds: float = IDLE_SLEEP_SECONDS,
) -> None:
    while True:
        processed = process_next_message(timeout=poll_timeout)
        if not processed:
            time.sleep(idle_sleep_seconds)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
    app = create_app()
    with app.app_context():
        redis_status = check_redis()
        db_status = check_database()
        LOGGER.info(
            "Worker bootstrap redis_ok=%s db_ok=%s",
            redis_status["ok"],
            db_status["ok"],
        )
        if not redis_status["ok"]:
            LOGGER.warning("Worker redis check error=%s", redis_status.get("error"))
        if not db_status["ok"]:
            LOGGER.warning("Worker database check error=%s", db_status.get("error"))

        run_forever()


if __name__ == "__main__":
    main()
