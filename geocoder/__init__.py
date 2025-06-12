import os

from flask import Flask

from . import views
from .database import db

dot_env = os.path.join(os.getcwd(), ".env")
if os.path.exists(dot_env):
    from dotenv import load_dotenv

    load_dotenv()


def create_app(app_config=None):
    """The application factory, used to generate the Flask instance."""
    app = Flask(__name__)
    database_uri = os.getenv("DATABASE_URI", "sqlite:///:memory:").replace("postgis", "postgresql+psycopg")

    if app_config:
        app.config.update(app_config)
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_uri
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    app.register_blueprint(views.bp)
    app.add_url_rule("/", endpoint="index")
    app.add_url_rule("/api/<object_id>", endpoint="detail")
    app.add_url_rule("/api/geocode", endpoint="geocode")
    app.add_url_rule("/livez", endpoint="liveness")
    app.add_url_rule("/readyz", endpoint="readiness")
    app.add_url_rule("/favicon.ico", endpoint="favicon")

    return app
