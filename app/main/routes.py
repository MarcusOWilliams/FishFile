from turtle import home
from flask import render_template
from app.main import bp


@bp.route('/')
@bp.route('/index')
def index():
    render_template('home.html')