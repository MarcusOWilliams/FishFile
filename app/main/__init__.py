#The initilisaion module for the main blueprint
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes