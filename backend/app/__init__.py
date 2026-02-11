from dotenv import load_dotenv
from flask import Flask

from .auth import init_auth
from .routes import api_bp
from .services.database import configure_database, db, migrate
from .services.redis import configure_redis

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    configure_database(app)
    configure_redis(app)

    db.init_app(app)

    from . import models  # noqa: F401

    migrate.init_app(app, db)
    init_auth(app)
    app.register_blueprint(api_bp)

    return app


app = create_app()
