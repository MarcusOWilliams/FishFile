
from flask import render_template
from app.main import bp
from flask_login import login_required


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('home.html')