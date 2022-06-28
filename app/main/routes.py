
from datetime import datetime


from app import db
from app.main import bp
from app.main import email
from app.models import Change, Fish, Notification, User, requires_roles
from flask import flash, redirect, render_template, url_for, g, session
from flask_login import current_user, login_required
from app.main.forms import SimpleSearch, NewFish, SettingsForm, FilterChanges, SearchFrom
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
    form = SearchFrom()
    if form.validate_on_submit():
        search_dict = {}
        for fieldname, value in form.data.items():
            if fieldname != "csrf_token" and fieldname != "submit":
                if value != None and value != '':
                    search_dict[fieldname] = value

        session['search_dict'] = search_dict.copy() 
        return redirect(url_for('main.search'))

    return render_template('index.html', form = form, title="Home Page")

@bp.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    form = SearchFrom()

    if form.validate_on_submit():
        search_dict = {}
        for fieldname, value in form.data.items():
            if fieldname != "csrf_token" and fieldname != "submit":
                if value != None and value != '':
                    search_dict[fieldname] = value

        session['search_dict'] = search_dict.copy() 
        return redirect(url_for('main.search'))

    search_dict = session['search_dict'].copy()
    session['search_dict'] = {}
    
    all_fish = Fish.query.filter(id != None).subquery()
    for key in search_dict:
        if key == "fish_id":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(fish_id = search_dict[key]).subquery()
        elif key == "tank_id":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(tank_id = search_dict[key]).subquery()
        elif key == "stock":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(stock = search_dict[key]).subquery()
        elif key == "status":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(status = search_dict[key]).subquery()
        elif key == "protocol":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(protocol= search_dict[key]).subquery()
        elif key == "source":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(source = search_dict[key]).subquery()
        elif key == "cross_type":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(cross_type = search_dict[key]).subquery()
        elif key == "birthday":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(birthday = search_dict[key]).subquery()
        elif key == "date_of_arrival":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(date_of_arrival = search_dict[key]).subquery()
        elif key == "user_code":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.user_code.has(code = search_dict[key])).subquery()
        elif key == "project_license":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.project_license_holder.has(project_license = search_dict[key])).subquery()
        elif key == "allele":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(allele = search_dict[key]).subquery()
        elif key == "mutant_gene":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(mutant_gene = search_dict[key]).subquery()
        elif key == "transgenes":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(transgenes = search_dict[key]).subquery()
        elif key == "father_id":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.father.has(fish_id = search_dict[key])).subquery()
        elif key == "father_stock":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.father.has(stock = search_dict[key])).subquery()
        elif key == "mother_id":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.mother.has(fish_id = search_dict[key])).subquery()
        elif key == "mother_stock":
            all_fish = Fish.query.select_entity_from(all_fish).filter(Fish.mother.has(stock = search_dict[key])).subquery()
        elif key == "total":
            all_fish = Fish.query.select_entity_from(all_fish).filter_by(total = search_dict[key]).subquery()
       
    
    all_fish = Fish.query.select_entity_from(all_fish).all()



    return render_template('search.html', form = form, all_fish=all_fish, search_dict = search_dict, title="Search")


@bp.route("/simplesearch/")
@login_required
def simplesearch():
    fish = Fish.query.filter_by(stock=g.search_form.search.data).first_or_404()
    if fish is None:
        pass

    return redirect(url_for('main.fish', id=fish.id))


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


    filter_list = filters.split(" ")
    if filters == "all":
        changes  = Change.query.filter_by(fish_id=id).order_by(Change.time.desc()).all()
    else:
        changes = []
        for filter in filter_list:
            changes += Change.query.filter_by(field = filter).all()

        #sort the list back into decending time order
        changes.sort(key=lambda x: x.time, reverse=True)


   
    

            
    return render_template('fishchanges.html', fish=fish, changes = changes, filters = filter_list, form=form, title = title)

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
             field = "fish_id",
             old = fish.fish_id, 
             new = form.fish_id.data)
            db.session.add(change)

            fish.fish_id = form.fish_id.data

        if fish.tank_id != form.tank_id.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "tank ID",
             field = "tank_id", 
             old = fish.tank_id, 
             new = form.tank_id.data)
            db.session.add(change)

            fish.tank_id = form.tank_id.data

        if fish.status != form.status.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "status",
             field = "status", 
             old =fish.status, 
             new =form.status.data)
            db.session.add(change)

            fish.status = form.status.data

        if fish.stock != form.stock.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "stock",
             field = "stock", 
             old =fish.stock , 
             new =form.stock.data)
            db.session.add(change)

            fish.stock = form.stock.data

        if fish.protocol != form.protocol.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "protocol",
             field = "protocol", 
             old = fish.protocol, 
             new =form.protocol.data)
            db.session.add(change)

            fish.protocol = form.protocol.data

        if fish.birthday != form.birthday.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "birthday",
             field = "birthday", 
             old = fish.birthday, 
             new =form.birthday.data)
            db.session.add(change)

            fish.birthday = form.birthday.data

        if fish.date_of_arrival != form.date_of_arrival.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "date of arrival", 
             field = "date_of_arrival",
             old = fish.date_of_arrival, 
             new =form.date_of_arrival.data)
            db.session.add(change)

            fish.date_of_arrival = form.date_of_arrival.data

        if fish.allele != form.allele.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "allele", 
             field = "allele",
             old = fish.allele, 
             new =form.allele.data)
            db.session.add(change)

            fish.allele = form.allele.data

        if fish.mutant_gene != form.mutant_gene.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "mutant gene",
             field = "mutant_gene", 
             old = fish.mutant_gene, 
             new =form.mutant_gene.data)
            db.session.add(change)

            fish.mutant_gene = form.mutant_gene.data

        if fish.transgenes != form.transgenes.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "transgenes",
             field = "transgenes", 
             old = fish.transgenes, 
             new =form.transgenes.data)
            db.session.add(change)

            fish.transgenes = form.transgenes.data

        if fish.cross_type != form.cross_type.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "cross type",
             field = "cross_type", 
             old = fish.cross_type, 
             new =form.cross_type.data)
            db.session.add(change)

            fish.cross_type = form.cross_type.data

        if fish.comments != form.comments.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "comments",
             field = "comments", 
             old = fish.comments, 
             new =form.comments.data)
            db.session.add(change)

            fish.comments = form.comments.data

        if fish.males != form.males.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of males",
             field = "males", 
             old = fish.males, 
             new =form.males.data)
            db.session.add(change)

            fish.males = form.males.data

        if fish.females != form.females.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of females",
             field = "females", 
             old = fish.females , 
             new =form.females.data)
            db.session.add(change)

            fish.females = form.females.data

        if fish.unsexed != form.unsexed.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of unsexed fish",
             field = "unsexed", 
             old = fish.unsexed, 
             new =form.unsexed.data)
            db.session.add(change)

            fish.unsexed = form.unsexed.data

        if fish.carriers != form.carriers.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of carriers", 
             field = "carriers",
             old = fish.carriers, 
             new =form.carriers.data)
            db.session.add(change)

            fish.carriers = form.carriers.data

        if fish.total != form.total.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "number of total fish",
             field = "total", 
             old = fish.total, 
             new =form.total.data)
            db.session.add(change)

            fish.total = form.total.data

        if fish.source != form.source.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "source",
             field = "source", 
             old = fish.source, 
             new =form.source.data)
            db.session.add(change)

            fish.source = form.source.data

        if fish.father.fish_id != form.father_id.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "father ID", 
             field = "father_id",
             old = f"{fish.father.fish_id}", 
             new =  f"{father.fish_id}",)
            db.session.add(change)
            fish.father = father

        if fish.father.stock!= form.father_stock.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "father stock", 
             field = "father_stock",
             old = f"{fish.father.stock}", 
             new =  f"{father.stock}",)
            db.session.add(change)
            fish.father = father

        if fish.mother.fish_id != form.mother_id.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "mother ID", 
             field = "mother_id",
             old = f"{fish.mother.fish_id}", 
             new =  f"{mother.fish_id}",)
            db.session.add(change)
            fish.mother = mother

        if fish.mother.stock!= form.mother_stock.data:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "mother stock", 
             field = "mother_stock",
             old = f"{fish.mother.stock}", 
             new =  f"{mother.stock}",)
            db.session.add(change)
            fish.father = mother

        if fish.user_code != fish_user:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "user code",
             field = "user_code", 
             old = fish.user_code.code, 
             new = fish_user.code)
            db.session.add(change)

            fish.user_code = fish_user

        if fish.project_license_holder != license_holder:
            change = Change(user = current_user, fish = fish, action = "Updated",
             contents = "project license",
             field = "project_license",
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
        g.search_form = SimpleSearch()
