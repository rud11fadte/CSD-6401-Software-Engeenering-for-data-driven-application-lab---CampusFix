
from pathlib import Path
from flask import Flask
from config import Config
from .db import init_db, close_db
from .web import register_routes

# Get the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent

def create_app(test_config=None):

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static")
    )

    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    init_db(app)

    app.teardown_appcontext(close_db)

    register_routes(app)

    return app
