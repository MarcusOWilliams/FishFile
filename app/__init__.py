import re
from flask import Flask
from config import Config


def create_app(config_Class = Config):
    app = Flask(__name__)
    app.config.from_object(config_Class)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app