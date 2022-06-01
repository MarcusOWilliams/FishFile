import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, 'environmentVariables.env'))

#this is the main configuration class which sets all of the variables needed to create the app, this class is used in the main app __init__ file
class Config(object):

    #secret key
    SECRET_KEY = os.environ.get('SECRET_KEY')

    #Linking the database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_POOL_RECYCLE = 299
    SQLALCHEMY_TRACK_MODIFICATIONS = False
