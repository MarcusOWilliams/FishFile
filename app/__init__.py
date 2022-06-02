from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

migrate = Migrate()

#For login manager
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = ('You must be signed in to access this page.')


bcrypt = Bcrypt()

def create_app(config_Class = Config):
    #generate the app with the specified configurations
    app = Flask(__name__)
    app.config.from_object(config_Class)

    #add the database and migration
    db.init_app(app)
    migrate.init_app(app,db)

    #add the login manager
    login.init_app(app)

    #add bcypt hashing capabilities
    bcrypt.init_app(app)


    #link the bluebrints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
