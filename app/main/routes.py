
from datetime import datetime
from xmlrpc.client import Boolean

from sqlalchemy import subquery


from app import db
from app.main import bp
from app.main import email
from app.models import Change, Fish, Notification, User, requires_roles
from flask import flash, redirect, render_template, url_for, g
from flask_login import current_user, login_required
from app.main.forms import SearchForm, NewFish, SettingsForm, FilterChanges
from app.main.email import send_notification_email
import sys
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
    changes = Change.query.filter_by(user=user).order_by(Change.time.desc()).all()
    user_fish = user.users_fish
    return render_template('user.html', user=user, changes=changes, user_fish = user_fish, title=title)


@bp.route('/fish/<id>')
@login_required
def fish(id):
    fish = Fish.query.filter_by(id=id).first_or_404()
    title = f"Fish ({fish.stock})"

    return render_template('fish.html', fish=fish, title=title)

@bp.route('/fish/<id>/changes/<filters>', methods=['GET', 'POST'])
@login_required
def fishchange(id, filters = "all"):
    fish = Fish.query.filter_by(id=id).first_or_404()
    form = FilterChanges()
    title = f"Fish History ({fish.stock})"
    if form.validate_on_submit():
        filters = []
        for fieldname, value in form.data.items():
            if value and (fieldname != "submit" and fieldname != "csrf_token"):
                filters.append(fieldname)

        if len(filters)<1:
            filters.append("all")
        return redirect(url_for('main.fishchange', id= fish.id, filters = " ".join(filters)))

    if filters == "all":
        changes  = Change.query.filter_by(fish_id=id).order_by(Change.time.desc()).all()
    else:
        filter_list = filters.split(" ")
        changes = Change.query.filter_by(fish_id=id).order_by(Change.time.desc()).subquery()
        for filter in filter_list:
            changes = Change.query.select_entity_from(changes).filter_by(contents = filter).subquery()

        changes = Change.query.select_entity_from(changes).all()
    

            
    return render_template('fishchanges.html', fish=fish, changes = changes, form=form, title = title)

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

            father = father,
            mother = mother,
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

@bp.route('/updatefish/<id>/', methods=['GET', 'POST'])
@login_required
def updatefish(id):
    form = NewFish()
    fish = Fish.query.filter_by(id=id).first_or_404()
    title = f"Update Fish ({fish.stock})"

    if form.validate_on_submit():

        father = Fish.query.filter_by(fish_id = form.father_id.data, stock = form.father_stock.data).first()
        mother = Fish.query.filter_by(fish_id = form.mother_id.data, stock = form.mother_stock.data).first()
        fish_user = User.query.filter_by(code = form.user_code.data).first()
        license_holder = User.query.filter_by(project_license = form.project_license.data).first()

    
        if fish.fish_id != form.fish_id.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "fish ID", 
             old = fish.fish_id, 
             new = form.fish_id.data)
            db.session.add(change)

            fish.fish_id = form.fish_id.data

        if fish.tank_id != form.tank_id.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "tank ID", 
             old = fish.tank_id, 
             new = form.tank_id.data)
            db.session.add(change)

            fish.tank_id = form.tank_id.data

        if fish.status != form.status.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "status", 
             old =fish.status, 
             new =form.status.data)
            db.session.add(change)

            fish.status = form.status.data

        if fish.stock != form.stock.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "stock", 
             old =fish.stock , 
             new =form.stock.data)
            db.session.add(change)

            fish.stock = form.stock.data

        if fish.protocol != form.protocol.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "protocol", 
             old = fish.protocol, 
             new =form.protocol.data)
            db.session.add(change)

            fish.protocol = form.protocol.data

        if fish.birthday != form.birthday.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "birthday", 
             old = fish.birthday, 
             new =form.birthday.data)
            db.session.add(change)

            fish.birthday = form.birthday.data

        if fish.date_of_arrival != form.date_of_arrival.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "date of arrival", 
             old = fish.date_of_arrival, 
             new =form.date_of_arrival.data)
            db.session.add(change)

            fish.date_of_arrival = form.date_of_arrival.data

        if fish.allele != form.allele.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "allele", 
             old = fish.allele, 
             new =form.allele.data)
            db.session.add(change)

            fish.allele = form.allele.data

        if fish.mutant_gene != form.mutant_gene.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "mutant gene", 
             old = fish.mutant_gene, 
             new =form.mutant_gene.data)
            db.session.add(change)

            fish.mutant_gene = form.mutant_gene.data

        if fish.transgenes != form.transgenes.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "transgenes", 
             old = fish.transgenes, 
             new =form.transgenes.data)
            db.session.add(change)

            fish.transgenes = form.transgenes.data

        if fish.cross_type != form.cross_type.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "cross type", 
             old = fish.cross_type, 
             new =form.cross_type.data)
            db.session.add(change)

            fish.cross_type = form.cross_type.data

        if fish.comments != form.comments.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "comments", 
             old = fish.comments, 
             new =form.comments.data)
            db.session.add(change)

            fish.comments = form.comments.data

        if fish.males != form.males.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of males", 
             old = fish.males, 
             new =form.males.data)
            db.session.add(change)

            fish.males = form.males.data

        if fish.females != form.females.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of females", 
             old = fish.females , 
             new =form.females.data)
            db.session.add(change)

            fish.females = form.females.data

        if fish.unsexed != form.unsexed.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of unsexed fish", 
             old = fish.unsexed, 
             new =form.unsexed.data)
            db.session.add(change)

            fish.unsexed = form.unsexed.data

        if fish.carriers != form.carriers.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of carriers", 
             old = fish.carriers, 
             new =form.carriers.data)
            db.session.add(change)

            fish.carriers = form.carriers.data

        if fish.total != form.total.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of total fish", 
             old = fish.total, 
             new =form.total.data)
            db.session.add(change)

            fish.total = form.total.data

        if fish.source != form.source.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "source", 
             old = fish.source, 
             new =form.source.data)
            db.session.add(change)

            fish.source = form.source.data

        if fish.father!= father:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "father", 
             old = f"ID:{fish.father.stock}, Stock: {fish.father.stock}", 
             new =  f"ID:{father.stock}, Stock: {father.stock}",)
            db.session.add(change)
            fish.father = father

        if fish.mother != mother:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "mother", 
             old = f"ID:{fish.mother.stock}, Stock: {fish.mother.stock}", 
             new =  f"ID:{mother.stock}, Stock: {mother.stock}",)
            db.session.add(change)
            fish.mother = mother

        if fish.user_code != fish_user:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "user code", 
             old = fish.user_code.code, 
             new = fish_user.code)
            db.session.add(change)

            fish.user_code = fish_user

        if fish.project_license_holder != license_holder:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "project license", 
             old =fish.project_license_holder.project_license, 
             new =license_holder.project_license)
            db.session.add(change)
            fish.project_license_holder = license_holder
        
        
        db.session.commit()
        flash("Fish updated", 'info')
        return redirect(url_for('main.fish', id = fish.id))
    
    return render_template("updatefish.html", fish=fish, form=form, title=title)

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
