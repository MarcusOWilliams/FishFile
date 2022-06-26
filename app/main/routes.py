
from datetime import datetime


from app import db
from app.main import bp
from app.main import email
from app.models import Change, Fish, Notification, User, requires_roles
from flask import flash, redirect, render_template, url_for, g
from flask_login import current_user, login_required
from app.main.forms import SearchForm, NewFish, SettingsForm
from app.main.email import send_notification_email
# this route defines the landing page of the website


@bp.route('/', methods=['GET', 'POST'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    return render_template('landing.html')

# this route defines the homepage of the website


@bp.route('/home', methods=['GET', 'POST'])
@login_required
def index():

    return render_template('index.html', title="Home Page")


@bp.route("/search/")
@login_required
def search():
    fish = Fish.query.filter_by(fish_id=g.search_form.search.data).all()
    if fish is None:
        return render_template('fishsearch.html')

    return render_template('fishsearch.html', fish_list=fish, title="Search")


@bp.route('/user/<username>/')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    title = user.username
    changes = Change.query.filter_by(user=user).all()
    user_fish = user.users_fish
    return render_template('user.html', user=user, changes=changes, user_fish = user_fish, title=title)


@bp.route('/fish/<id>')
@login_required
def fish(id):
    fish = Fish.query.filter_by(id=id).first_or_404()
    title = f"Fish ({fish.stock})"

    return render_template('fish.html', fish=fish, title=title)

@bp.route('/allfish')
@login_required
def allfish():
    all_fish = Fish.query.all()

    return render_template('allfish.html', all_fish=all_fish, title="All Fish")

@bp.route('/newfish/', methods=['GET', 'POST'])
@login_required
def newfish():
    form = NewFish()
    if form.validate_on_submit():
        father = Fish.query.filter_by(fish_id = form.father_id.data, stock = form.father_stock.data).first()
        mother = Fish.query.filter_by(fish_id = form.mother_id.data, stock = form.mother_stock.data).first()
        fish_user = User.query.filter_by(email = form.user_code.data).first()
        license_holder = User.query.filter_by(project_license = form.project_license.data).first()
        
        newfish = Fish(
            fish_id = form.fish_id.data,
            tank_id = form.tank_id.data,
            status = form.status.data,
            stock = form.stock.data,
            protocol = form.protocol.data,
            birthday = form.birthday.data,
            date_of_arrival = form.date_of_arrival.data,
            allele = form.allele.data,
            mutant_gene = form.mutant_gene.data,
            transgenes = form.transgenes.data,
            cross_type = form.cross_type.data,
            comments = form.comments.data,
            males = form.males.data,
            females = form.females.data,
            unsexed = form.unsexed.data,
            carriers = form.carriers.data,
            total = form.total.data,
            source = form.source.data,

            father_id = father.id,
            mother_id = mother.id,
            user_code= fish_user,
            project_license_holder = license_holder
        )
        db.session.add(newfish)

        change = Change(user = current_user, fish = newfish, action = "Added")
        db.session.add(change)

        db.session.commit()
        flash("The new fish has been added to the database", 'info')
        return redirect(url_for('main.fish', id = newfish.id))

    return render_template('newfish.html',form=form, title="New Fish")


@bp.route('/settings/', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    current_settings = current_user.settings
    if form.validate_on_submit():
        current_user.settings.emails = form.emails.data
        db.session.commit()
        flash("Settings Applied", 'info')
        n = Notification(category="Updated", user=current_user)
        send_notification_email(current_user, n)

        return redirect(url_for('main.user', username=current_user.username))

    return render_template('settings.html', form=form, current_settings=current_settings)


# This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()
