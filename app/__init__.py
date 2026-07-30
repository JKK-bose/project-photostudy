from flask import Flask
from .database import init_db


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "photostudio-practice-secret-key-2026"

    init_db()

    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
