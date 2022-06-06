
from flask import render_template
from app import db
from app.main import bp
from flask_login import login_required, current_user
from datetime import datetime


@bp.route('/')
@bp.route('/index')
@login_required
def index():
    return render_template('index.html', title ="Home Page")


#This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()