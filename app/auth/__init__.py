#The initilisaion module for authentication the blueprint
from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes