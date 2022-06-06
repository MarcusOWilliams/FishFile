from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_moment import Moment

#The database is run using SQLAlchemy
db = SQLAlchemy()

#Allows migration of database changes
migrate = Migrate()

#For login manager
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = ('You must be signed in to access this page.')

#For password hashing
bcrypt = Bcrypt()

#For sending emails
mail = Mail()

#For nice datetime formatiing
moment = Moment()

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

    #add email support
    mail.init_app(app)

    #Link moment for datetime 
    moment.init_app(app)

    #link the bluebrints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    return app
