import re
from flask import Flask
from config import Config


def create_app(config_Class = Config):
    app = Flask(__name__)
    app.config.from_object(config_Class)


    return app