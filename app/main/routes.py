
from datetime import datetime
from turtle import title

from app import db
from app.main import bp
from app.models import Fish, User, requires_roles
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

    return render_template('fishsearch.html', fish_list = fish, title="Search")

@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    title = user.username

    return render_template('user.html', user=user, title=title)
    

# This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()

