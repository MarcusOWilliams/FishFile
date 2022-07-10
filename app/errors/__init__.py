#The initilisaion module for the errors blueprint
from flask import Blueprint

bp = Blueprint('errors', __name__)

from app.errors import handlers