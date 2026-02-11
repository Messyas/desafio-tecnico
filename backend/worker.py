import time

from app import create_app
from app.services.database import check_database
from app.services.redis import check_redis

IDLE_SLEEP_SECONDS = 30


def main() -> None:
    app = create_app()
    with app.app_context():
        redis_status = check_redis()
        db_status = check_database()
        print(
            "Worker bootstrap | "
            f"redis_ok={redis_status['ok']} db_ok={db_status['ok']}"
        )
        if not redis_status["ok"]:
            print(f"Worker redis check error={redis_status.get('error')}")
        if not db_status["ok"]:
            print(f"Worker database check error={db_status.get('error')}")

        while True:
            time.sleep(IDLE_SLEEP_SECONDS)


if __name__ == "__main__":
    main()
