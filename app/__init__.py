from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

migrate = Migrate()



def create_app(config_Class = Config):
    #generate the app with the specified configurations
    app = Flask(__name__)
    app.config.from_object(config_Class)

    #add the database and migration
    db.init_app(app)
    migrate.init_app(app)


    #link the bluebrints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app