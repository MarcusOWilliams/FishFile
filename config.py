import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# this is the main configuration class which sets all of the variables needed to create the app, this class is used in the main app __init__ file
class Config(object):
    WEBSITE_NAME = os.environ.get('WEBSITE_NAME')
    # secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Linking the database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 299,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    FISH_PER_PAGE = int(os.environ.get('FISH_PER_PAGE')) or 5
    CHANGES_PER_PAGE = int(os.environ.get('CHANGES_PER_PAGE')) or 10

    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'UTC'

    FISH_PICTURES = os.path.join(os.getcwd(), os.environ.get('FISH_PICTURE_FOLDER'))
    PERSONAL_LICENSES = os.path.join(os.getcwd(), os.environ.get('PERSONAL_LICENSES_FOLDER'))
    PROJECT_LICENSES = os.path.join(os.getcwd(), os.environ.get('PROJECT_LICENSES_FOLDER'))

