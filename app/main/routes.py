
from datetime import datetime

from app import db
from app.main import bp
from app.models import Fish, requires_roles
from flask import flash, redirect, render_template, url_for, g
from flask_login import current_user, login_required
from app.main.forms import SearchForm

#this route defines the homepage of the website
@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    
    return render_template('index.html', title="Home Page")


@bp.route("/search")
@login_required
def search():
    fish = Fish.query.filter_by(fish_id = g.search_form.search.data).all()
    if fish is None:
        return render_template('fishsearch.html')

    return render_template('fishsearch.html', fish_list = fish)

    

# This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

