
from datetime import datetime
from email import message
from os import abort
from turtle import title





from app import db
from app.main import bp
from app.main import email
from app.models import Allele, Change, Fish, Notification, Reminder, User, requires_roles
from flask import (
    flash,
    redirect,
    render_template,
    url_for,
    jsonify,
    g,
    session,
    request,
    current_app,
)
from flask_login import current_user, login_required
from app.main.forms import (
    AlleleForm,
    EmptyForm,
    OrderForm,
    SimpleSearch,
    NewFish,
    SettingsForm,
    FilterChanges,
    SearchFrom,
    RoleChange
)
from app.main.email import send_notification_email, send_reminder_email
import sys

# this route defines the landing page of the website


@bp.route("/", methods=["GET", "POST"])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    return render_template("landing.html")


# this route defines the homepage of the website


@bp.route("/home", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def index():
    form = SearchFrom()
    if form.validate_on_submit():
        search_dict = {}
        for fieldname, value in form.data.items():
            if fieldname != "csrf_token" and fieldname != "submit":
                if value != None and value != "":
                    search_dict[fieldname] = value
                    
        session["order_by"] = form.order.data
        session["search_dict"] = search_dict.copy()
        return redirect(url_for("main.search"))

    return render_template("index.html", form=form, title="Home Page")


@bp.route("/search", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def search():
    form = SearchFrom()



    if form.validate_on_submit():
        search_dict = {}
        for fieldname, value in form.data.items():
            if fieldname != "csrf_token" and fieldname != "submit":
                if value != None and value != "":
                    search_dict[fieldname] = value

        session["order_by"] = form.order.data
        session["search_dict"] = search_dict.copy()
        

        return redirect(url_for("main.search"))


    search_dict = session["search_dict"].copy()

    all_fish = Fish.query.filter(id != None).subquery()
    for key in search_dict:
        if key == "fish_id":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(fish_id=search_dict[key])
                .subquery()
            )
        elif key == "tank_id":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(tank_id=search_dict[key])
                .subquery()
            )
        elif key == "stock":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(stock=search_dict[key])
                .subquery()
            )
        elif key == "status":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(status=search_dict[key])
                .subquery()
            )
        elif key == "protocol":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(protocol=search_dict[key])
                .subquery()
            )
        elif key == "source":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(source=search_dict[key])
                .subquery()
            )
        elif key == "cross_type":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(cross_type=search_dict[key])
                .subquery()
            )
        elif key == "birthday":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(birthday=search_dict[key])
                .subquery()
            )
        elif key == "date_of_arrival":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(date_of_arrival=search_dict[key])
                .subquery()
            )
        elif key == "user_code":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.user_code.has(code=search_dict[key]))
                .subquery()
            )
        elif key == "project_license":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(
                    Fish.project_license_holder.has(project_license=search_dict[key])
                )
                .subquery()
            )
        elif key == "allele":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(allele=search_dict[key])
                .subquery()
            )
        elif key == "mutant_gene":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(mutant_gene=search_dict[key])
                .subquery()
            )
        elif key == "transgenes":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(transgenes=search_dict[key])
                .subquery()
            )
        elif key == "father_id":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.father.has(fish_id=search_dict[key]))
                .subquery()
            )
        elif key == "father_stock":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.father.has(stock=search_dict[key]))
                .subquery()
            )
        elif key == "mother_id":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.mother.has(fish_id=search_dict[key]))
                .subquery()
            )
        elif key == "mother_stock":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.mother.has(stock=search_dict[key]))
                .subquery()
            )
        elif key == "total":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(total=search_dict[key])
                .subquery()
            )

        
    page = request.args.get("page", 1, type=int)

    #set the order of the fish, if not set they are sorted by most recently added
    order = session.get("order_by", "Newest Added")

    

    if order == "Age ( young -> old )":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.birthday.desc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
        
    elif order == "Age (old -> young)":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.birthday.asc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Fish ID":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.fish_id.asc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
        
    elif order == "Tank ID":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.tank_id.asc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Stock":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.stock.asc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Newest Added":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.added.desc())
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    else:
        result = Fish.query.select_entity_from(all_fish)
        all_results = result.all()
        all_fish = result.paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )

    next_url = (
        url_for("main.search", page=all_fish.next_num) if all_fish.has_next else None
    )
    prev_url = (
        url_for("main.search", page=all_fish.prev_num) if all_fish.has_prev else None
    )

    for field in form:
        if field.name != "csrf_token" and field.name != "submit":
            if search_dict.get(field.name) != None and search_dict.get(field.name) != "":
                field.data = search_dict[field.name]
                    
        
    return render_template(
        "search.html",
        form=form,
        all_fish=all_fish.items,
        search_dict=search_dict,
        title="Search",
        next_url=next_url,
        prev_url=prev_url,
        pagination=all_fish,
        all_results=all_results
    )


@bp.route("/simplesearch/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def simplesearch():
    fish = Fish.query.filter_by(tank_id=g.search_form.search.data.upper()).filter(Fish.status!="Dead").first()
    if fish is None:
        return redirect(url_for("main.fish", id=-1))

    return redirect(url_for("main.fish", id=fish.id))


@bp.route("/user/<username>/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    title = user.username
    user_fish = Fish.query.filter_by(user_code=user).filter(Fish.status != "Dead").order_by(Fish.added.desc()).all()
    changes = Change.query.filter_by(user=user).order_by(Change.time.desc()).all()

    page = request.args.get("page", 1, type=int)
    changes = (
        Change.query.filter_by(user=user)
        .order_by(Change.time.desc())
        .paginate(page, current_app.config["CHANGES_PER_PAGE"], False)
    )

    next_url = (
        url_for("main.user", username=username, page=changes.next_num)
        if changes.has_next
        else None
    )
    prev_url = (
        url_for("main.user", username=username, page=changes.prev_num)
        if changes.has_prev
        else None
    )

    roleForm = RoleChange()

    if current_user.isOwner():
        roleForm.role.choices = ["","Blocked", "User", "Researcher", "Admin", "Owner"]
    elif current_user.isAdmin():
        roleForm.role.choices =  ["","Blocked", "User", "Researcher"]

    
    if roleForm.validate_on_submit():
        if not current_user.isAdmin:
            abort(403)
        user.role = roleForm.role.data
        db.session.commit()
        return redirect(url_for('main.user', username = user.username))

    
    roleForm.role.data = user.role
    

    return render_template(
        "user.html",
        user=user,
        changes=changes.items,
        user_fish=user_fish,
        title=title,
        pagination=changes,
        next_url=next_url,
        prev_url=prev_url,
        roleForm = roleForm
    )


@bp.route("/fish/<id>")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def fish(id):
    fish = Fish.query.filter_by(id=id).first()
    alleles = Allele.query.filter_by(fish=fish)
    if fish is None:
        title = "Fish Not Found"
    else:
        title = f"Fish ({fish.stock})"
    

    return render_template("fish.html", fish=fish, title=title,alleles=alleles, form = EmptyForm())


@bp.route("/fish/<id>/changes/<filters>", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def fishchange(id, filters="all"):
    fish = Fish.query.filter_by(id=id).first_or_404()
    form = FilterChanges()
    title = f"Fish History ({fish.stock})"
    if form.validate_on_submit():
        filters = []
        for fieldname, value in form.data.items():
            if value and (fieldname != "submit" and fieldname != "csrf_token"):
                filters.append(fieldname)

        if len(filters) < 1:
            filters.append("all")

        return redirect(
            url_for("main.fishchange", id=fish.id, filters=" ".join(filters))
        )

    page = request.args.get("page", 1, type=int)

    filter_list = filters.split(" ")
    if filters == "all":
        changes = (
            Change.query.filter_by(fish_id=id)
            .order_by(Change.time.desc())
            .paginate(page, current_app.config["CHANGES_PER_PAGE"], False)
        )
    else:
        for filter in filter_list:
            if "changes" in locals():
                changes = changes.union(Change.query.filter_by(field=filter))
            else:
                changes = Change.query.filter_by(field=filter)

        changes = changes.order_by(Change.time.desc()).paginate(
            page, current_app.config["CHANGES_PER_PAGE"], False
        )

    next_url = (
        url_for("main.fishchange", id=fish.id, filters=filters, page=changes.next_num)
        if changes.has_next
        else None
    )
    prev_url = (
        url_for("main.fishchange", id=fish.id, filters=filters, page=changes.prev_num)
        if changes.has_prev
        else None
    )

    return render_template(
        "fishchanges.html",
        fish=fish,
        changes=changes.items,
        filters=filter_list,
        form=form,
        title=title,
        pagination=changes,
        next_url=next_url,
        prev_url=prev_url,
    )

@bp.route("/fish/<id>/history/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def fishhistory(id):
    fish = Fish.query.filter_by(id=id).first_or_404()

    ancestors = fish.get_ancestors(0)
    generations = max(ancestors, key = lambda x:x['level'])['level']

    return render_template("fishhistory.html", fish = fish, generations = generations, current_generation =0, title="Fish History")

@bp.route("/fish/<id>/updatealleles/", methods=["GET", "POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def updatealleles(id):
    fish = Fish.query.filter_by(id=id).first_or_404()
    alleles = Allele.query.filter_by(fish=fish).all()

    if request.method == "POST":

        for allele in alleles:
            
            allele.unidentified= request.form.get(f"{allele.name.replace(' ', '')}Unidentified") == "on"

            allele.identified = request.form.get(f"{allele.name.replace(' ', '')}Identified") == "on"

            allele.heterozygous = request.form.get(f"{allele.name.replace(' ', '')}Heterozygous") == "on"

            allele.homozygous = request.form.get(f"{allele.name.replace(' ', '')}Homozygous") == "on"

            allele.hemizygous = request.form.get(f"{allele.name.replace(' ', '')}Hemizygous") == "on"


        db.session.commit()

        return redirect(url_for("main.fish", id=fish.id))
    
        

    return render_template('updatealleles.html', fish=fish, alleles = alleles, title = "Update Alleles")


@bp.route("/newfish/", methods=["GET", "POST"])
@login_required
@requires_roles("Admin", "Owner")
def newfish():
    form = NewFish()

    all_users = User.query.filter_by(is_verified=True).all()
    user_codes = [""] + [user.code for user in all_users]
    form.user_code.choices = sorted(user_codes)

    licenses_values = [user.project_license for user in all_users]
    licenses = [""] + list(filter(None, licenses_values))
    form.project_license.choices = sorted(licenses)

    

    if form.validate_on_submit():
        father = Fish.query.filter_by(
            fish_id=form.father_id.data, stock=form.father_stock.data
        ).first()
        mother = Fish.query.filter_by(
            fish_id=form.mother_id.data, stock=form.mother_stock.data
        ).first()
        fish_user = User.query.filter_by(code=form.user_code.data).first()
        license_holder = User.query.filter_by(
            project_license=form.project_license.data
        ).first()
       

        newfish = Fish(
            fish_id=form.fish_id.data,
            tank_id=form.tank_id.data.upper(),
            status=form.status.data,
            stock=form.stock.data.upper(),
            protocol=form.protocol.data,
            birthday=form.birthday.data,
            date_of_arrival=form.date_of_arrival.data,
            mutant_gene=form.mutant_gene.data,
            transgenes=form.transgenes.data,
            cross_type=form.cross_type.data,
            comments=form.comments.data,
            links = form.links.data,
            males=form.males.data,
            females=form.females.data,
            unsexed=form.unsexed.data,
            carriers=form.carriers.data,
            total=form.total.data,
            source=form.source.data,
            father=father,
            mother=mother,
            user_code=fish_user,
            project_license_holder=license_holder,
            
        )
        db.session.add(newfish)
        for name in form.allele.data:
            allele = Allele(name = name, fish=newfish)
            db.session.add(allele)

        change = Change(user=current_user, fish=newfish, action="Added")
        db.session.add(change)

        

        if form.alert_date.data or form.alert_msg.data:
            reminder = Reminder(user = newfish.user_code, fish = newfish, date=form.alert_date.data, message=form.alert_msg.data)
            db.session.add(reminder)
            if reminder.date <= datetime.today().date():
                reminder.send_reminder()
        

        if newfish.user_code.settings.add_notifications:
            notification = Notification(user=newfish.user_code, fish=newfish, category="Added", contents="A new fish under your user code has been added")
            db.session.add(notification)
            notification.send_email()

        if newfish.project_license_holder.settings.pl_add_notifications and newfish.user_code != newfish.project_license_holder:
            pl_notification = Notification(user=newfish.project_license_holder, fish=newfish, category="Added", contents="A new fish under your project license has been added") 
            db.session.add(pl_notification)
            pl_notification.send_email()
        
        db.session.commit()
        flash("The new fish has been added to the database", "info")
        return redirect(url_for("main.fish", id=newfish.id))


    return render_template("newfish.html", form=form, title="New Fish")


@bp.route("/updatefish/<id>/", methods=["GET", "POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def updatefish(id):
    form = NewFish()
    deleteReminderForm = EmptyForm()
    fish = Fish.query.filter_by(id=id).first_or_404()
    title = f"Update Fish ({fish.stock})"

    all_users = User.query.filter_by(is_verified=True).all()
    user_codes = [""] + [user.code for user in all_users]
    form.user_code.choices = sorted(user_codes)

    licenses_values = [user.project_license for user in all_users]
    licenses = [""] + list(filter(None, licenses_values))
    form.project_license.choices = sorted(licenses)

    current_alleles = [allele.name for allele in fish.alleles]

    if form.validate_on_submit():

        father = Fish.query.filter_by(
            fish_id=form.father_id.data, stock=form.father_stock.data
        ).first()
        mother = Fish.query.filter_by(
            fish_id=form.mother_id.data, stock=form.mother_stock.data
        ).first()
        fish_user = User.query.filter_by(code=form.user_code.data).first()
        license_holder = User.query.filter_by(
            project_license=form.project_license.data
        ).first()

        
        notification = Notification(fish=fish, category="Change", contents="Changes have been made to one of your fish entries")


        change_count=0
        if fish.fish_id != form.fish_id.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="fish ID",
                field="fish_id",
                old=fish.fish_id,
                new=form.fish_id.data,
                notification = notification
            )
            db.session.add(change)
            
            fish.fish_id = form.fish_id.data
            change_count+=1
            

        if fish.tank_id != form.tank_id.data.upper():
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="tank ID",
                field="tank_id",
                old=fish.tank_id,
                new=form.tank_id.data.upper(),
                notification = notification
            )
            db.session.add(change)
            
            fish.tank_id = form.tank_id.data.upper()
            change_count+=1


        if fish.status != form.status.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="status",
                field="status",
                old=fish.status,
                new=form.status.data,
                notification = notification
            )
            db.session.add(change)
            change_count+=1
            fish.status = form.status.data

        if fish.stock != form.stock.data.upper():
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="stock",
                field="stock",
                old=fish.stock,
                new=form.stock.data.upper(),
                notification = notification
            )
            db.session.add(change)
            change_count+=1

            fish.stock = form.stock.data.upper()

        if fish.protocol != form.protocol.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="protocol",
                field="protocol",
                old=fish.protocol,
                new=form.protocol.data,
                notification = notification
            )
            db.session.add(change)
            change_count+=1
            fish.protocol = form.protocol.data

        if fish.birthday != form.birthday.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="birthday",
                field="birthday",
                old=fish.birthday,
                new=form.birthday.data,
                notification = notification
            )
            db.session.add(change)

            fish.birthday = form.birthday.data
            change_count+=1


        if fish.date_of_arrival != form.date_of_arrival.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="date of arrival",
                field="date_of_arrival",
                old=fish.date_of_arrival,
                new=form.date_of_arrival.data,
                notification = notification
            )
            db.session.add(change)

            fish.date_of_arrival = form.date_of_arrival.data
            change_count+=1



        if fish.mutant_gene != form.mutant_gene.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="mutant gene",
                field="mutant_gene",
                old=fish.mutant_gene,
                new=form.mutant_gene.data,
                notification = notification
            )
            db.session.add(change)

            fish.mutant_gene = form.mutant_gene.data
            change_count+=1


        if fish.transgenes != form.transgenes.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="transgenes",
                field="transgenes",
                old=fish.transgenes,
                new=form.transgenes.data,
                notification = notification
            )
            db.session.add(change)

            fish.transgenes = form.transgenes.data
            change_count+=1


        if fish.cross_type != form.cross_type.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="cross type",
                field="cross_type",
                old=fish.cross_type,
                new=form.cross_type.data,
                notification = notification
            )
            db.session.add(change)

            fish.cross_type = form.cross_type.data
            change_count+=1


        if fish.comments != form.comments.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="comments",
                field="comments",
                old=fish.comments,
                new=form.comments.data,
                notification = notification
            )
            db.session.add(change)

            fish.comments = form.comments.data
            change_count+=1

        if fish.links != form.links.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="links",
                field="links",
                notification = notification
            )
            db.session.add(change)

            fish.links = form.links.data
            change_count+=1

        if fish.males != form.males.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of males",
                field="males",
                old=fish.males,
                new=form.males.data,
                notification = notification
            )
            db.session.add(change)

            fish.males = form.males.data
            change_count+=1


        if fish.females != form.females.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of females",
                field="females",
                old=fish.females,
                new=form.females.data,
                notification = notification
            )
            db.session.add(change)

            fish.females = form.females.data
            change_count+=1


        if fish.unsexed != form.unsexed.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of unsexed fish",
                field="unsexed",
                old=fish.unsexed,
                new=form.unsexed.data,
                notification = notification
            )
            db.session.add(change)

            fish.unsexed = form.unsexed.data
            change_count+=1


        if fish.carriers != form.carriers.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of carriers",
                field="carriers",
                old=fish.carriers,
                new=form.carriers.data,
                notification = notification
            )
            db.session.add(change)

            fish.carriers = form.carriers.data
            change_count+=1


        if fish.total != form.total.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of total fish",
                field="total",
                old=fish.total,
                new=form.total.data,
                notification = notification
            )
            db.session.add(change)
            change_count+=1


            fish.total = form.total.data

        if fish.source != form.source.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="source",
                field="source",
                old=fish.source,
                new=form.source.data,
                notification = notification
            )
            db.session.add(change)
            change_count+=1


            fish.source = form.source.data

        if fish.father.fish_id != form.father_id.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="father ID",
                field="father_id",
                old=f"{fish.father.fish_id}",
                new=f"{father.fish_id}",
                notification = notification
            )
            db.session.add(change)
            fish.father = father
            change_count+=1


        if fish.father.stock != form.father_stock.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="father stock",
                field="father_stock",
                old=f"{fish.father.stock}",
                new=f"{father.stock}",
                notification = notification
            )
            db.session.add(change)
            change_count+=1

            fish.father = father

        if fish.mother.fish_id != form.mother_id.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="mother ID",
                field="mother_id",
                old=f"{fish.mother.fish_id}",
                new=f"{mother.fish_id}",
                notification = notification
            )
            db.session.add(change)
            change_count+=1

            fish.mother = mother

        if fish.mother.stock != form.mother_stock.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="mother stock",
                field="mother_stock",
                old=f"{fish.mother.stock}",
                new=f"{mother.stock}",
                notification = notification
            )
            db.session.add(change)
            change_count+=1

            fish.father = mother

        if fish.user_code != fish_user:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="user code",
                field="user_code",
                old=fish.user_code.code,
                new=fish_user.code,
                notification = notification
            )
            db.session.add(change)
            change_count+=1


            fish.user_code = fish_user

        if fish.project_license_holder != license_holder:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="project license",
                field="project_license",
                old=fish.project_license_holder.project_license,
                new=license_holder.project_license,
                notification = notification
            )
            db.session.add(change)
            fish.project_license_holder = license_holder
            change_count+=1
        

        if current_alleles != form.allele.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="allele",
                field="allele",
                old=", ".join(current_alleles),
                new=", ".join(form.allele.data),
                notification = notification
            )
            db.session.add(change)

            Allele.query.filter_by(fish=fish).delete()

            for name in form.allele.data:
                allele =Allele(name=name, fish=fish)
                db.session.add(allele)

            change_count+=1

        
                

        if change_count>0:
            notification.change_count = change_count

            if fish.user_code.settings.change_notifications:
                notification.user = fish.user_code
                notification.send_email()
                db.session.add(notification)
                db.session.commit()
            
            flash("Fish updated", "info")

        if form.alert_date.data or form.alert_msg.data:
            reminder = Reminder(user = fish.user_code, fish = fish, date=form.alert_date.data, message=form.alert_msg.data)
            db.session.add(reminder)

            if reminder.date <= datetime.today().date():
                reminder.send_reminder()


            db.session.commit()

        return redirect(url_for("main.fish", id=fish.id))


    if fish.project_license_holder != None:
        form.project_license.data = fish.project_license_holder.project_license
    if fish.user_code != None:
        form.user_code.data = fish.user_code.code
    if fish.status != None:
        form.status.data = fish.status
    if fish.source != None:
        form.source.data = fish.source

    form.comments.data = fish.comments
    form.allele.data = current_alleles

    

    return render_template("updatefish.html", fish=fish, form=form, title=title, deleteReminderForm =deleteReminderForm )

@bp.route("/allfish/", methods=["GET", "POST"])
@login_required
@requires_roles("Admin", "Owner")
def allfish():

    form = OrderForm()
    
    

    if form.validate_on_submit():
        session["order_by"] = form.order.data

        return redirect(url_for('main.allfish'))

    

    #set the order of the fish, if not set they are sorted by most recently added
    order = session.get("order_by", "Newest Added")

    
    form.order.data = order

    if order == "Age ( young -> old )":
        fish = Fish.query.order_by(Fish.birthday.desc()).all()
    elif order == "Age (old -> young)":
        fish = Fish.query.order_by(Fish.birthday.asc()).all()
    elif order == "Fish ID":
        fish = Fish.query.order_by(Fish.fish_id.asc()).all()

    elif order == "Tank ID":
        fish = Fish.query.order_by(Fish.tank_id.asc()).all()

    elif order == "Stock":
        fish = Fish.query.order_by(Fish.stock.asc()).all()
    elif order == "Newest Added":
        fish = Fish.query.order_by(Fish.added.desc()).all()
    else:
        fish = Fish.query.all()
    
        
    

    return render_template('allfish.html', all_fish = fish, form = form)

@bp.route("/projectlicense/<license>/", methods=["GET", "POST"])
@login_required
@requires_roles("User","Researcher", "Admin", "Owner")
def project_license(license):

    form = OrderForm()

    
    if form.validate_on_submit():
        
        session["order_by"]=form.order.data

        return redirect(url_for('main.project_license', license=license))

    user = User.query.filter_by(project_license=license).first_or_404()

    page = request.args.get("page", 1, type=int)

    fish = Fish.query.filter_by(project_license_holder = user).paginate(
        page, current_app.config["FISH_PER_PAGE"], False
    )

    order = session.get("order_by", "Newest Added")

    form.order.data = order

    if order == "Age ( young -> old )":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.birthday.desc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Age (old -> young)":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.birthday.asc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Fish ID":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.fish_id.asc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Tank ID":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.tank_id.asc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Stock":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.stock.asc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    elif order == "Newest Added":
        fish = Fish.query.filter_by(project_license_holder = user).order_by(Fish.added.desc()).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )
    else:
        
        fish = Fish.query.filter_by(project_license_holder = user).paginate(
                page, current_app.config["FISH_PER_PAGE"], False
            )

    next_url = (
        url_for("main.project_license", license=license, page=fish.next_num) if fish.has_next else None
    )
    prev_url = (
        url_for("main.project_license", license=license, page=fish.prev_num) if fish.has_prev else None
    )
    

    return render_template("projectlicense.html", fish_list=fish.items ,user=user, next_url=next_url, prev_url=prev_url, pagination=fish, form=form)


@bp.route("/settings/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def settings():
    form = SettingsForm()
    current_settings = current_user.settings

    

    if form.validate_on_submit():
        current_user.settings.emails = form.emails.data
        current_user.settings.email_reminders = form.email_reminders.data

        current_user.settings.add_notifications = form.add_notifications.data
        current_user.settings.change_notifications = form.change_notifications.data
        current_user.settings.turnover_notifications = form.turnover_notifications.data
        current_user.settings.age_notifications = form.age_notifications.data

        current_user.settings.pl_add_notifications = form.pl_add_notifications.data
        current_user.settings.pl_turnover_notifications = form.pl_turnover_notifications.data
        current_user.settings.pl_age_notifications = form.pl_age_notifications.data
        
        if current_user.project_license != form.project_license.data:
            fish = Fish.query.filter_by(project_license_holder = current_user).all()
            old_license = current_user.project_license
            current_user.project_license = form.project_license.data
            for f in fish:
                
                change = Change(
                    user=current_user,
                    fish=f,
                    action="Updated",
                    contents="project license",
                    field="project_license",
                    old= old_license,
                    new=current_user.project_license
                )
                db.session.add(change)
                f.project_license_holder = current_user



        db.session.commit()

        flash("Settings Applied", "info")

        return redirect(url_for("main.settings"))

    if current_user.project_license is not None:
        form.project_license.data = current_user.project_license

    return render_template(
        "settings.html", form=form, current_settings=current_settings
    )

@bp.route("/guides/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def guides():

    return render_template("guides.html", title="Guides")

@bp.route("/userlist/")
@requires_roles("Owner")
@login_required
def user_list():
    users = User.query.order_by(User.id.desc())

    return render_template('Admin/user_list.html',users=users)


@bp.route('/reset_notifications', methods=['POST'])
@login_required
def reset_notifications():
    current_user.last_notification_read_time = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "reset"})

@bp.route('/deletefish/<id>', methods=['POST'])
@login_required
@requires_roles("Admin", "Owner")
def deletefish(id):
    fish = Fish.query.filter_by(id=id).first()
    db.session.delete(fish)
    db.session.commit()
    flash("The entry has been deleted", 'info')
    return redirect(url_for('main.index'))

@bp.route('/deletereminder/<id>', methods=['POST'])
@login_required
@requires_roles("Researcher","Admin", "Owner")
def deletereminder(id):
    reminder = Reminder.query.filter_by(id=id).first()
    fish_id = reminder.fish.id
    db.session.delete(reminder)
    db.session.commit()

    flash("The reminder has been deleted", 'info')
    return redirect(url_for('main.updatefish', id=fish_id))

# This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SimpleSearch()
