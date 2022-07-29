from datetime import datetime
from os import abort


from wtforms.validators import DataRequired, ValidationError


from app import db
from app.main import bp
from app.main import email
from app.models import (
    Allele,
    Change,
    Fish,
    Notification,
    Reminder,
    User,
    get_all_allele_names,
    get_all_user_codes,
    get_all_user_licenses,
    requires_roles,
    Photo,
)
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
    EditAlleles,
    EmptyForm,
    OrderForm,
    PhotoCaptionForm,
    SimpleSearch,
    NewFish,
    SettingsForm,
    FilterChanges,
    SearchFrom,
    RoleChange,
)
import os
from werkzeug.utils import secure_filename
import urllib.parse


"""
This function describes the route for /
There are no permissions required for this route
This route is used for loading the page a user first sees when they load the website
If a user is logged in they are redirected to /index
"""


@bp.route("/", methods=["GET", "POST"])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    return render_template("landing.html")


"""
This function describes the route for /home
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for the home page of a logged in user
This route contains a main search form which redirects to /search when submitted
"""


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

    form.status.data = "Alive"

    return render_template("index.html", form=form, title="Home Page")


"""
This function describes the route for /search
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for showing results of a user's search
This route contains a search form which updates the search and reloads the page
"""


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
                .filter_by(tank_id=search_dict[key].upper())
                .subquery()
            )
        elif key == "stock":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter_by(stock=search_dict[key].upper())
                .subquery()
            )
        elif key == "status":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.status.contains(search_dict[key]))
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
        elif key == "age_older":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.months >= search_dict[key], Fish.status != "Dead")
                .subquery()
            )

        elif key == "age_younger":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.months < search_dict[key], Fish.status != "Dead")
                .subquery()
            )

        elif key == "user_code":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .join(Fish.user_code, aliased=True)
                .filter(User.code.contains(search_dict[key]))
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
            for search in search_dict[key].split(","):
                search = search.strip()
                all_fish = (
                    Fish.query.select_entity_from(all_fish)
                    .join(Fish.alleles, aliased=True)
                    .filter(Allele.name == search)
                    .subquery()
                )
        elif key == "mutant_gene":
            for search in search_dict[key].split(","):
                search = search.strip()
                all_fish = (
                    Fish.query.select_entity_from(all_fish)
                    .filter(Fish.mutant_gene.contains(search))
                    .subquery()
                )
        elif key == "transgenes":
            for search in search_dict[key].split(","):
                search = search.strip()
                all_fish = (
                    Fish.query.select_entity_from(all_fish)
                    .filter(Fish.transgenes.contains(search))
                    .subquery()
                )

        elif key == "total":
            all_fish = (
                Fish.query.select_entity_from(all_fish)
                .filter(Fish.total >= search_dict[key])
                .subquery()
            )

    page = request.args.get("page", 1, type=int)

    # set the order of the fish, if not set they are sorted by most recently added
    order = session.get("order_by", "Newest Added")

    if order == "Age ( young -> old )":
        result = (
            Fish.query.select_entity_from(all_fish)
            .filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.desc())
        )
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)

    elif order == "Age (old -> young)":
        result = (
            Fish.query.select_entity_from(all_fish)
            .filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.asc())
        )
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)
    elif order == "Fish ID":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.fish_id.asc())
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)

    elif order == "Tank ID":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.tank_id.asc())
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)
    elif order == "Stock":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.stock.asc())
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)
    elif order == "Newest Added":
        result = Fish.query.select_entity_from(all_fish).order_by(Fish.added.desc())
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)
    else:
        result = Fish.query.select_entity_from(all_fish)
        all_results = result.all()
        all_fish = result.paginate(page, current_app.config["FISH_PER_PAGE"], False)

    next_url = (
        url_for("main.search", page=all_fish.next_num) if all_fish.has_next else None
    )
    prev_url = (
        url_for("main.search", page=all_fish.prev_num) if all_fish.has_prev else None
    )

    for field in form:

        if field.name not in ("csrf_token", "submit", "birthday", "date_of_arrival"):
            if (
                search_dict.get(field.name) != None
                and search_dict.get(field.name) != ""
            ):
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
        all_results=all_results,
    )


"""
This function describes the route for /simplesearch
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for when a user uses the simple search bar
The user is redirected to the fish route after findin (or not) the match
"""


@bp.route("/simplesearch/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def simplesearch():
    fish = (
        Fish.query.filter_by(tank_id=g.search_form.search.data.upper())
        .filter(Fish.status != "Dead")
        .first()
    )
    if fish is None:
        return redirect(url_for("main.fish", id=-1))

    return redirect(url_for("main.fish", id=fish.id))


"""
This function describes the route for /user
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for displaying the profile page of a given user
This page contains all of the entries a user is working on and all of the changes they have made
"""


@bp.route("/user/<username>/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def user(username):
    user = User.query.filter_by(username=username, is_verified=True).first()

    if user is None:
        return render_template("errors/user_not_found.html", title = "User Not Found")


    title = user.username
    user_fish = (
        Fish.query.filter_by(user_code=user)
        .filter(Fish.status != "Dead")
        .order_by(Fish.added.desc())
        .all()
    )
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
        roleForm.role.choices = ["", "Blocked", "User", "Researcher", "Admin", "Owner"]
    elif current_user.isAdmin():
        roleForm.role.choices = ["", "Blocked", "User", "Researcher"]

    if roleForm.validate_on_submit():
        if not current_user.isAdmin:
            abort(403)
        user.role = roleForm.role.data
        db.session.commit()
        return redirect(url_for("main.user", username=user.username))

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
        roleForm=roleForm,
    )


"""
This function describes the route for /fish
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for displaying a fish entry and its related data
"""


@bp.route("/fish/<id>")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def fish(id):
    fish = Fish.query.filter_by(id=id).first_or_404()
    alleles = Allele.query.filter_by(fish=fish).all()
    if fish is None:
        title = "Fish Not Found"
    else:
        title = f"Fish ({fish.stock})"

    if fish.system == "Old":

        return render_template("oldfish.html", fish=fish, title=title, form=EmptyForm())

    return render_template(
        "fish.html", fish=fish, title=title, alleles=alleles, form=EmptyForm()
    )


"""
This function describes the route for /fish/id/changes
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for showing the backlog of changes made to a fish entry
"""


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
                changes = Change.query.filter_by(field=filter, fish_id=id)

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


"""
This function describes the route for /fish/id/hisstory
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for displaying the family tree of a given fish entry
"""


@bp.route("/fish/<id>/history/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def fishhistory(id):
    fish = Fish.query.filter_by(id=id).first_or_404()

    ancestors = fish.get_ancestors(0)
    generations = max(ancestors, key=lambda x: x["level"])["level"]

    return render_template(
        "fishhistory.html",
        fish=fish,
        generations=generations,
        current_generation=0,
        title="Family Tree",
    )


"""
This function describes the route for /fish/id/updatealleles
Permission required for this route are "Researcher", "Admin", "Owner"
This route is used for updating the status of the alleles of a given fish entry
"""


@bp.route("/fish/<id>/updatealleles/", methods=["GET", "POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def updatealleles(id):
    fish = Fish.query.filter_by(id=id).first_or_404()
    alleles = Allele.query.filter_by(fish=fish).all()

    if request.method == "POST":

        for allele in alleles:

            allele.unidentified = (
                request.form.get(f"{allele.name.replace(' ', '')}Unidentified") == "on"
            )

            allele.identified = (
                request.form.get(f"{allele.name.replace(' ', '')}Identified") == "on"
            )

            allele.heterozygous = (
                request.form.get(f"{allele.name.replace(' ', '')}Heterozygous") == "on"
            )

            allele.homozygous = (
                request.form.get(f"{allele.name.replace(' ', '')}Homozygous") == "on"
            )

            allele.hemizygous = (
                request.form.get(f"{allele.name.replace(' ', '')}Hemizygous") == "on"
            )

        db.session.commit()

        return redirect(url_for("main.fish", id=fish.id))

    return render_template(
        "updatealleles.html", fish=fish, alleles=alleles, title="Update Alleles"
    )


"""
This function describes the route for /newfish
Permission required for this route are "Admin", "Owner"
This route is used for adding new fish to the database
"""


@bp.route("/newfish/", methods=["GET", "POST"])
@login_required
@requires_roles("Admin", "Owner")
def newfish():
    form = NewFish()

    form.user_code.choices = [""] + get_all_user_codes()

    form.project_license.choices = [""] + get_all_user_licenses()

    form.allele.choices = sorted(list(get_all_allele_names()))

    if form.validate_on_submit():
        # both mother and father get the most recently added match, incase there are multiple matches
        father = (
            Fish.query.filter_by(
                tank_id=form.father_tank_id.data.upper(),
                stock=form.father_stock.data.upper(),
            )
            .order_by(Fish.id.desc())
            .first()
        )
        mother = (
            Fish.query.filter_by(
                tank_id=form.mother_tank_id.data.upper(),
                stock=form.mother_stock.data.upper(),
            )
            .order_by(Fish.id.desc())
            .first()
        )


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
            links=form.links.data,
            males=form.males.data,
            females=form.females.data,
            unsexed=form.unsexed.data,
            carriers=form.carriers.data,
            total=form.total.data,
            source=form.source.data,
            father=father,
            mother=mother
        )
        db.session.add(newfish)

        if form.project_license.data != None and form.project_license.data != "":
            license_holder = User.query.filter_by(
                project_license=form.project_license.data
                ).first()
        else:
            license_holder = None

        if form.user_code.data != None and form.user_code.data != "":
            fish_user = User.query.filter_by(code=form.user_code.data).first()
        else:
            fish_user = None

        if license_holder is None:
            newfish.old_license = form.custom_license.data
        else:
            newfish.project_license_holder = license_holder

        if fish_user is None:
            newfish.old_code = form.custom_code.data
        else:
            newfish.user_code = fish_user

        for name in form.allele.data:
            allele = Allele(name=name, fish=newfish)
            db.session.add(allele)

        change = Change(user=current_user, fish=newfish, action="Added")
        db.session.add(change)

        if form.origin_tank_id.data != None and form.origin_tank_id.data != "":
            # ordered to get the most recently added match
            origin_tank = (
                Fish.query.filter_by(
                    tank_id=form.origin_tank_id.data.upper(),
                    stock=form.origin_tank_stock.data.upper(),
                )
                .order_by(Fish.id.desc())
                .first()
            )
            if origin_tank != None:
                newfish.origin = origin_tank

        if form.alert_date.data or form.alert_msg.data:
            if fish_user is not None:
                reminder = Reminder(
                    user=fish_user,
                    fish=newfish,
                    date=form.alert_date.data,
                    message=form.alert_msg.data,
                )
                db.session.add(reminder)
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()

            if license_holder is not None:
                reminder = Reminder(
                    user=license_holder,
                    fish=newfish,
                    date=form.alert_date.data,
                    message=form.alert_msg.data,
                )
                db.session.add(reminder)
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()

        if fish_user is not None:
            if newfish.user_code.settings.add_notifications:
                notification = Notification(
                    user=newfish.user_code,
                    fish=newfish,
                    category="Added",
                    contents="A new fish under your user code has been added",
                )
                db.session.add(notification)
                notification.send_email()
                
        if license_holder is not None:
            if (
                newfish.project_license_holder.settings.pl_add_notifications
                and newfish.user_code != newfish.project_license_holder
            ):
                pl_notification = Notification(
                    user=newfish.project_license_holder,
                    fish=newfish,
                    category="Added",
                    contents="A new fish under your project license has been added",
                )
                db.session.add(pl_notification)
                pl_notification.send_email()

        file_names = [file.filename for file in form.photos.data]

        if file_names != [""] and file_names != None:

            for photo in form.photos.data:
                file = photo
                filename = secure_filename(f"{newfish.id}_{file.filename}")
                file.save(os.path.join(current_app.config["FISH_PICTURES"], filename))
                photo = Photo(fish=newfish, name=filename)
                db.session.add(photo)

        newfish.months = newfish.getMonths()

        db.session.commit()
        flash("The new fish has been added to the database", "info")
        return redirect(url_for("main.fish", id=newfish.id))

    form.source.data = "Home"

    return render_template("newfish.html", form=form, title="New Fish")


"""
This function describes the route for /updatefish
Permission required for this route are  "Researcher", "Admin", "Owner"
This route is used for updating the attributes for a fish entry
"""


@bp.route("/updatefish/<id>/", methods=["GET", "POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def updatefish(id):

    form = NewFish()
    deleteReminderForm = EmptyForm()
    deletePhotoForm = EmptyForm()
    fish = Fish.query.filter_by(id=id).first_or_404()
    title = f"Update Fish ({fish.stock})"

    if not current_user.isOwner():
        if (
            current_user != fish.project_license_holder
            or current_user != fish.user_code
        ):
            flash(
                "You do not have permission to update this fish, you must be associted by either user code or own the project license to update this entry",
                "warning",
            )
            return redirect(url_for("main.fish", id=fish.id))

    form.user_code.choices = [""] + get_all_user_codes()

    form.project_license.choices = [""] + get_all_user_licenses()

    form.allele.choices = sorted(list(get_all_allele_names()))

    current_alleles = [allele.name for allele in fish.alleles]

    if form.validate_on_submit():

        father = (
            Fish.query.filter_by(
                tank_id=form.father_tank_id.data.upper(),
                stock=form.father_stock.data.upper(),
            )
            .order_by(Fish.id.desc())
            .first()
        )
        mother = (
            Fish.query.filter_by(
                tank_id=form.mother_tank_id.data.upper(),
                stock=form.mother_stock.data.upper(),
            )
            .order_by(Fish.id.desc())
            .first()
        )

        if form.project_license.data != None and form.project_license.data != "":
            license_holder = User.query.filter_by(
                project_license=form.project_license.data
                ).first()
        else:
            license_holder = None

        if form.user_code.data != None and form.user_code.data != "":
            fish_user = User.query.filter_by(code=form.user_code.data).first()
        else:
            fish_user = None

        origin_tank = (
            Fish.query.filter_by(
                tank_id=form.origin_tank_id.data.upper(),
                stock=form.origin_tank_stock.data.upper(),
            )
            .order_by(Fish.id.desc())
            .first()
        )

        pictures = [file.filename for file in form.photos.data]

        # if a fish is being updated from the old system the process is different
        # all fields are updated to the new system
        if fish.system == "Old":

            fish.system = "New"
            fish.fish_id = form.fish_id.data
            fish.tank_id = form.tank_id.data.upper()
            fish.status = form.status.data
            fish.stock = form.stock.data.upper()
            fish.protocol = form.protocol.data
            fish.birthday = form.birthday.data
            fish.months = fish.getMonths()
            fish.date_of_arrival = form.date_of_arrival.data
            fish.mutant_gene = form.mutant_gene.data
            fish.transgenes = form.transgenes.data
            fish.cross_type = form.cross_type.data
            fish.comments = form.comments.data
            fish.links = form.links.data
            fish.males = form.males.data
            fish.females = form.females.data
            fish.unsexed = form.unsexed.data
            fish.carriers = form.carriers.data
            fish.total = form.total.data
            fish.source = form.source.data
            fish.father = father
            fish.mother = mother
            fish.origin = origin_tank
            if fish_user is not None:
                fish.user_code = fish_user
                fish.old_code = None
            else:
                fish.old_code = form.custom_code.data
            if license_holder is not None:
                fish.project_license_holder = license_holder
                fish.old_license = None
            else:
                fish.old_license = form.custom_license.data

            fish.old_mID = None
            fish.old_fID = None
            fish.old_fStock = None
            fish.old_mStock = None
            fish.old_birthday = None
            fish.old_arrival = None
            fish.old_allele = None

            for name in form.allele.data:
                allele = Allele(name=name, fish=fish)
                db.session.add(allele)

            for photo in form.photos.data:
                if photo is None or photo.filename == "":
                    continue
                file = photo
                filename = secure_filename(f"{fish.id}_{file.filename}")
                current = Photo.query.filter_by(fish=fish, name=filename).first()
                if current == None:
                    file.save(
                        os.path.join(current_app.config["FISH_PICTURES"], filename)
                    )
                    photo = Photo(fish=fish, name=filename)
                    db.session.add(photo)
                else:
                    current.delete()
                    file.save(
                        os.path.join(current_app.config["FISH_PICTURES"], filename)
                    )
                    photo = Photo(fish=fish, name=filename)
                    db.session.add(photo)

            if form.alert_date.data or form.alert_msg.data:
                reminder = Reminder(
                    user=fish.user_code,
                    fish=fish,
                    date=form.alert_date.data,
                    message=form.alert_msg.data,
                )
                db.session.add(reminder)

                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()

            notification = Notification(
                fish=fish,
                category="Change",
                contents="Changes have been made to one of your fish entries",
            )

            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="system",
                field="system",
                old="New",
                new="Old",
                notification=notification,
            )

            db.session.add(change)
            if fish.user_code.settings.change_notifications:
                notification.user = fish.user_code
                notification.change_count = 1
                notification.send_email()
                db.session.add(notification)
                db.session.commit()

            db.session.commit()

            return redirect(url_for("main.fish", id=fish.id))

        notification = Notification(
            fish=fish,
            category="Change",
            contents="Changes have been made to one of your fish entries",
        )

        change_count = 0
        if fish.fish_id != form.fish_id.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="fish ID",
                field="fish_id",
                old=fish.fish_id,
                new=form.fish_id.data,
                notification=notification,
            )
            db.session.add(change)

            fish.fish_id = form.fish_id.data
            change_count += 1

        if fish.tank_id != form.tank_id.data.upper():
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="tank ID",
                field="tank_id",
                old=fish.tank_id,
                new=form.tank_id.data.upper(),
                notification=notification,
            )
            db.session.add(change)

            fish.tank_id = form.tank_id.data.upper()
            change_count += 1

        if fish.status != form.status.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="status",
                field="status",
                old=fish.status,
                new=form.status.data,
                notification=notification,
            )
            db.session.add(change)
            change_count += 1
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
                notification=notification,
            )
            db.session.add(change)
            change_count += 1

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
                notification=notification,
            )
            db.session.add(change)
            change_count += 1
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
                notification=notification,
            )
            db.session.add(change)

            fish.birthday = form.birthday.data
            fish.months = fish.getMonths()
            change_count += 1

        if fish.date_of_arrival != form.date_of_arrival.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="date of arrival",
                field="date_of_arrival",
                old=fish.date_of_arrival,
                new=form.date_of_arrival.data,
                notification=notification,
            )
            db.session.add(change)

            fish.date_of_arrival = form.date_of_arrival.data
            change_count += 1

        if fish.mutant_gene != form.mutant_gene.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="mutant gene",
                field="mutant_gene",
                old=fish.mutant_gene,
                new=form.mutant_gene.data,
                notification=notification,
            )
            db.session.add(change)

            fish.mutant_gene = form.mutant_gene.data
            change_count += 1

        if fish.transgenes != form.transgenes.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="transgenes",
                field="transgenes",
                old=fish.transgenes,
                new=form.transgenes.data,
                notification=notification,
            )
            db.session.add(change)

            fish.transgenes = form.transgenes.data
            change_count += 1

        if fish.cross_type != form.cross_type.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="cross type",
                field="cross_type",
                old=fish.cross_type,
                new=form.cross_type.data,
                notification=notification,
            )
            db.session.add(change)

            fish.cross_type = form.cross_type.data
            change_count += 1

        if fish.comments != form.comments.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="comments",
                field="comments",
                old=fish.comments,
                new=form.comments.data,
                notification=notification,
            )
            db.session.add(change)

            fish.comments = form.comments.data
            change_count += 1

        if fish.links != form.links.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="links",
                field="links",
                notification=notification,
            )
            db.session.add(change)

            fish.links = form.links.data
            change_count += 1

        if fish.males != form.males.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of males",
                field="males",
                old=fish.males,
                new=form.males.data,
                notification=notification,
            )
            db.session.add(change)

            fish.males = form.males.data
            change_count += 1

        if fish.females != form.females.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of females",
                field="females",
                old=fish.females,
                new=form.females.data,
                notification=notification,
            )
            db.session.add(change)

            fish.females = form.females.data
            change_count += 1

        if fish.unsexed != form.unsexed.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of unsexed fish",
                field="unsexed",
                old=fish.unsexed,
                new=form.unsexed.data,
                notification=notification,
            )
            db.session.add(change)

            fish.unsexed = form.unsexed.data
            change_count += 1

        if fish.carriers != form.carriers.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of carriers",
                field="carriers",
                old=fish.carriers,
                new=form.carriers.data,
                notification=notification,
            )
            db.session.add(change)

            fish.carriers = form.carriers.data
            change_count += 1

        if fish.total != form.total.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="number of total fish",
                field="total",
                old=fish.total,
                new=form.total.data,
                notification=notification,
            )

            if (
                form.total_change_comment.data != None
                and form.total_change_comment.data != ""
            ):
                change.note = form.total_change_comment.data

            db.session.add(change)

            change_count += 1

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
                notification=notification,
            )
            db.session.add(change)
            change_count += 1

            fish.source = form.source.data

        if fish.father != father:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="father",
                old=f"{fish.father}",
                new=f"{father}",
                notification=notification,
            )
            db.session.add(change)
            fish.father = father
            change_count += 1

        if fish.mother != mother:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="mother",
                old=f"{fish.mother}",
                new=f"{mother}",
                notification=notification,
            )
            db.session.add(change)
            fish.mother = mother
            change_count += 1

        if fish.origin != origin_tank:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="origin",
                old=f"{fish.origin}",
                new=f"{origin_tank}",
                notification=notification,
            )
            db.session.add(change)
            change_count += 1

            fish.origin = origin_tank

        if fish.user_code != fish_user:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="user code",
                field="user_code",
                notification=notification,
            )
            if fish.user_code is not None:
                change.old = fish.user_code.code
            elif fish.old_code is not None:
                change.old = fish.old_code
            
            if fish_user is not None:
                change.new = fish_user.code
            elif form.custom_code.data != None or form.custom_code.data != "":
                change.new = form.custom_code.data

            db.session.add(change)
            change_count += 1

            fish.user_code = fish_user


        if fish_user is None:
            if fish.old_code != form.custom_code.data:
                change = Change(
                    user=current_user,
                    fish=fish,
                    action="Updated",
                    contents="user code",
                    field="user_code",
                    notification=notification,
                )
                if fish.user_code is not None:
                    change.old = fish.user_code.code
                elif fish.old_code is not None:
                    change.old = fish.old_code
                
                if fish_user is not None:
                    change.new = fish_user.code
                elif form.custom_code.data != None or form.custom_code.data != "":
                    change.new = form.custom_code.data
                db.session.add(change)
                change_count += 1

                fish.old_code = form.custom_code.data

        if fish.project_license_holder != license_holder:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="project license",
                field="project_license",
                notification=notification,
            )

            if fish.project_license_holder is not None:
                change.old = fish.project_license_holder.project_license
            elif fish.old_license is not None:
                change.old = fish.old_license
            
            if license_holder is not None:
                change.new = license_holder.project_license
            elif form.custom_license.data != None or form.custom_license.data != "":
                change.new = form.custom_license.data


            db.session.add(change)
            fish.project_license_holder = license_holder
            change_count += 1
        
        if license_holder is None:
            if fish.old_license != form.custom_license.data:
                change = Change(
                    user=current_user,
                    fish=fish,
                    action="Updated",
                    contents="user code",
                    field="user_code",
                    notification=notification,
                )
                if fish.project_license_holder is not None:
                    change.old = fish.project_license_holder.project_license
                elif fish.old_license is not None:
                    change.old = fish.old_license
                
                if license_holder is not None:
                    change.new = license_holder.project_license
                elif form.custom_license.data != None or form.custom_license.data != "":
                    change.new = form.custom_license.data

                db.session.add(change)
                change_count += 1

                fish.old_license = form.custom_license.data

        if current_alleles != form.allele.data:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="allele",
                field="allele",
                old=", ".join(current_alleles),
                new=", ".join(form.allele.data),
                notification=notification,
            )
            db.session.add(change)

            Allele.query.filter_by(fish=fish).delete()

            for name in form.allele.data:
                allele = Allele(name=name, fish=fish)
                db.session.add(allele)

            change_count += 1

        if pictures != None and pictures != [""]:
            change = Change(
                user=current_user,
                fish=fish,
                action="Updated",
                contents="photos",
                field="photos",
                notification=notification,
            )
            db.session.add(change)
            change_count += 1

            for photo in form.photos.data:
                file = photo
                filename = secure_filename(f"{fish.id}_{file.filename}")
                current = Photo.query.filter_by(fish=fish, name=filename).first()
                if current == None:
                    file.save(
                        os.path.join(current_app.config["FISH_PICTURES"], filename)
                    )
                    photo = Photo(fish=fish, name=filename)
                    db.session.add(photo)
                else:
                    current.delete()
                    file.save(
                        os.path.join(current_app.config["FISH_PICTURES"], filename)
                    )
                    photo = Photo(fish=fish, name=filename)
                    db.session.add(photo)

        if change_count > 0:
            notification.change_count = change_count
            if fish.user_code != None:
                if fish.user_code.settings.change_notifications:
                    notification.user = fish.user_code
                    notification.send_email()
                    db.session.add(notification)
                    db.session.commit()

            flash("Fish updated", "info")

        if form.alert_date.data or form.alert_msg.data:
            if fish_user is not None:
                reminder = Reminder(
                    user=fish_user,
                    fish=fish,
                    date=form.alert_date.data,
                    message=form.alert_msg.data,
                )
                db.session.add(reminder)
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()

            if license_holder is not None:
                reminder = Reminder(
                    user=license_holder,
                    fish=fish,
                    date=form.alert_date.data,
                    message=form.alert_msg.data,
                )
                db.session.add(reminder)
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()

            db.session.commit()

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
    form.links.data = fish.links
    form.mutant_gene.data = fish.mutant_gene
    form.transgenes.data = fish.transgenes

    return render_template(
        "updatefish.html",
        fish=fish,
        form=form,
        title=title,
        deleteReminderForm=deleteReminderForm,
        deletePhotoForm=deletePhotoForm,
    )


"""
This function describes the route for /allfish
Permission required for this route are  "Admin", "Owner"
This route is used for displaying a list of all fish in the database
"""


@bp.route("/allfish/", methods=["GET", "POST"])
@login_required
@requires_roles("Admin", "Owner")
def allfish():

    form = OrderForm()

    if form.validate_on_submit():
        session["order_by"] = form.order.data

        return redirect(url_for("main.allfish"))

    # set the order of the fish, if not set they are sorted by most recently added
    order = session.get("order_by", "Newest Added")

    form.order.data = order

    if order == "Age ( young -> old )":
        fish = (
            Fish.query.filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.desc())
            .all()
        )
    elif order == "Age (old -> young)":
        fish = (
            Fish.query.filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.asc())
            .all()
        )
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

    return render_template("allfish.html", all_fish=fish, form=form, title="All Fish")


"""
This function describes the route for /projectlicense
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for showing all of the fish associated with a project license
It also has links to the associated documents
"""


@bp.route("/projectlicense/<license>/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def project_license(license):

    form = OrderForm()

    if form.validate_on_submit():

        session["order_by"] = form.order.data

        return redirect(url_for("main.project_license", license=license))

    user = User.query.filter_by(project_license=license).first_or_404()

    page = request.args.get("page", 1, type=int)

    order = session.get("order_by", "Newest Added")

    form.order.data = order

    if order == "Age ( young -> old )":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.desc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Age (old -> young)":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .filter(Fish.birthday != None, Fish.status != "Dead")
            .order_by(Fish.birthday.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Fish ID":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .order_by(Fish.fish_id.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Tank ID":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .order_by(Fish.tank_id.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Stock":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .order_by(Fish.stock.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Newest Added":
        fish = (
            Fish.query.filter_by(project_license_holder=user)
            .order_by(Fish.added.desc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    else:

        fish = Fish.query.filter_by(project_license_holder=user).paginate(
            page, current_app.config["FISH_PER_PAGE"], False
        )

    next_url = (
        url_for("main.project_license", license=license, page=fish.next_num)
        if fish.has_next
        else None
    )
    prev_url = (
        url_for("main.project_license", license=license, page=fish.prev_num)
        if fish.has_prev
        else None
    )

    return render_template(
        "projectlicense.html",
        fish_list=fish.items,
        user=user,
        next_url=next_url,
        prev_url=prev_url,
        pagination=fish,
        form=form,
        title=f"Project License ({license})",
    )


"""
This function describes the route for /stock
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for showing all the fish associated with a stock
"""


@bp.route("/stock/<stock>/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def stock(stock):

    form = OrderForm()

    if form.validate_on_submit():

        session["order_by"] = form.order.data

        return redirect(url_for("main.stock", stock=stock))

    page = request.args.get("page", 1, type=int)

    order = session.get("order_by", "Newest Added")

    form.order.data = order

    if order == "Age ( young -> old )":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead", Fish.birthday != None)
            .order_by(Fish.birthday.desc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Age (old -> young)":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead", Fish.birthday != None)
            .order_by(Fish.birthday.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Fish ID":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead")
            .order_by(Fish.fish_id.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Tank ID":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead")
            .order_by(Fish.tank_id.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Stock":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead")
            .order_by(Fish.stock.asc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    elif order == "Newest Added":
        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead")
            .order_by(Fish.added.desc())
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    else:

        fish = (
            Fish.query.filter_by(stock=stock)
            .filter(Fish.status != "Dead")
            .paginate(page, current_app.config["FISH_PER_PAGE"], False)
        )
    current_total = 0
    for entry in fish.items:
        current_total += entry.total

    next_url = (
        url_for("main.stock", stock=stock, page=fish.next_num)
        if fish.has_next
        else None
    )
    prev_url = (
        url_for("main.stock", stock=stock, page=fish.prev_num)
        if fish.has_prev
        else None
    )

    return render_template(
        "stock.html",
        fish_list=fish.items,
        next_url=next_url,
        prev_url=prev_url,
        pagination=fish,
        form=form,
        title=f"Stock ({stock})",
        current_total=current_total,
        stock=stock,
    )


"""
This function describes the route for /stock/changes
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for showing all the changes associated with the total of fish belonging to a stock
"""


@bp.route("/stock/<stock>/changes/<filters>", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def stock_changes(stock, filters="all"):

    form = FilterChanges()

    if form.validate_on_submit():
        filters = []
        for fieldname, value in form.data.items():
            if value and (fieldname != "submit" and fieldname != "csrf_token"):
                filters.append(fieldname)

        if len(filters) < 1:
            filters.append("all")

        return redirect(
            url_for("main.stock_changes", stock=stock, filters=" ".join(filters))
        )

    page = request.args.get("page", 1, type=int)

    filter_list = filters.split(" ")

    if filters == "all":
        changes = (
            Change.query.filter(Change.fish.has(stock=stock))
            .order_by(Change.time.desc())
            .paginate(page, current_app.config["CHANGES_PER_PAGE"], False)
        )
    else:
        for filter in filter_list:
            if "changes" in locals():
                changes = changes.union(Change.query.filter_by(field=filter))
            else:
                changes = Change.query.filter_by(field=filter).filter(
                    Change.fish.has(stock=stock)
                )

        changes = changes.order_by(Change.time.desc()).paginate(
            page, current_app.config["CHANGES_PER_PAGE"], False
        )

    next_url = (
        url_for("main.stock_changes", stock=stock, page=changes.next_num)
        if changes.has_next
        else None
    )
    prev_url = (
        url_for("main.stock_changes", stock=stock, page=changes.prev_num)
        if changes.has_prev
        else None
    )
    return render_template(
        "stock_changes.html",
        form=form,
        title=f"{stock} changes",
        changes=changes.items,
        stock=stock,
        pagination=changes,
        next_url=next_url,
        prev_url=prev_url,
        filters=filter_list
    )


"""
This function describes the route for /settings
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for changing a users settings
"""


@bp.route("/settings/", methods=["GET", "POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def settings():
    form = SettingsForm()
    deletePersonalForm = EmptyForm()
    current_settings = current_user.settings

    if form.validate_on_submit():
        current_user.settings.emails = form.emails.data
        current_user.settings.email_reminders = form.email_reminders.data
        current_user.settings.pl_email_reminders = form.email_reminders.data


        current_user.settings.add_notifications = form.add_notifications.data
        current_user.settings.change_notifications = form.change_notifications.data
        current_user.settings.custom_reminder = form.custom_reminders.data
        current_user.settings.age_notifications = form.age_notifications.data

        current_user.settings.pl_add_notifications = form.pl_add_notifications.data
        current_user.settings.pl_custom_reminder = form.pl_custom_reminders.data
        current_user.settings.pl_age_notifications = form.pl_age_notifications.data

        current_user.personal_license = form.personal_license.data

        if current_user.project_license != form.project_license.data:
            fish = Fish.query.filter_by(project_license_holder=current_user).all()
            old_license = current_user.project_license
            current_user.project_license = form.project_license.data

            for f in fish:

                change = Change(
                    user=current_user,
                    fish=f,
                    action="Updated",
                    contents="project license",
                    field="project_license",
                    old=old_license,
                    new=current_user.project_license,
                )
                db.session.add(change)
                f.project_license_holder = current_user

        if form.personal_license_file.data:
            file = form.personal_license_file.data
            if file.filename != "":
                current_user.delete_personal_document()
                filename = secure_filename(f"{current_user.id}.pdf")
                file.save(
                    os.path.join(current_app.config["PERSONAL_LICENSES"], filename)
                )
                current_user.personal_document = True
                db.session.commit()

        if form.project_license_file.data:
            file = form.project_license_file.data
            if file.filename != "":
                current_user.delete_project_document()
                filename = secure_filename(f"{current_user.id}.pdf")
                file.save(
                    os.path.join(current_app.config["PROJECT_LICENSES"], filename)
                )
                current_user.project_document = True

        db.session.commit()

        flash("Settings Applied", "info")

        return redirect(url_for("main.settings"))

    if current_user.project_license is not None:
        form.project_license.data = current_user.project_license

    if current_user.personal_license is not None:
        form.personal_license.data = current_user.personal_license

    return render_template(
        "settings.html",
        form=form,
        current_settings=current_settings,
        deletePersonalForm=deletePersonalForm,
        title="Settings",
    )


"""
This function describes the route for /fish/photo/editcaption
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for updating the caption of a photo associated with a fish
"""


@bp.route("/fish/<fish_id>/photo/<photo_id>/editcaption/", methods=["GET", "POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def editcaption(fish_id, photo_id):
    fish = Fish.query.filter_by(id=fish_id).first_or_404()
    photo = Photo.query.filter_by(id=photo_id).first_or_404()
    form = PhotoCaptionForm()

    if form.validate_on_submit():
        photo.caption = form.caption.data
        db.session.commit()

        return redirect(url_for("main.fish", id=fish.id))

    if photo.caption != None and photo.caption != "":
        form.caption.data = photo.caption

    return render_template(
        "editcaption.html", form=form, fish=fish, photo=photo, title="Edit Caption"
    )


"""
This function describes the route for /guides
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for displaying all of the tutorials to a user
"""


@bp.route("/guides/")
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def guides():

    return render_template("guides.html", title="Guides")


"""
This function describes the route for /userlist
Permission required for this route are  "Owner"
This route is used for showing a site owner a list of all users
"""


@bp.route("/userlist/")
@requires_roles("Owner")
@login_required
def user_list():
    users = User.query.order_by(User.id.desc())

    return render_template("Admin/user_list.html", users=users, title="User List")


"""
This function describes the route for /editalleles
Permission required for this route are "Admin", "Owner"
This route is used for allowing an admin to update the list of alleles
"""


@bp.route("/editalleles/", methods=["GET", "POST"])
@login_required
@requires_roles("Admin", "Owner")
def edit_alleles():

    form = EditAlleles()
    allele_list = sorted(list(get_all_allele_names()))

    if form.validate_on_submit():
        if form.add.data != None and form.add.data != "":
            new_allele = Allele(name=form.add.data)
            db.session.add(new_allele)

        if form.remove.data != None and form.remove.data != "":
            remove_all = Allele.query.filter_by(name=form.remove.data).all()

            for allele in remove_all:
                db.session.delete(allele)

        db.session.commit()
        return redirect(url_for("main.edit_alleles"))

    return render_template(
        "edit_alleles.html", allele_list=allele_list, form=form, title="Edit Alleles"
    )


"""
This function describes the route for /reset_notifications
This route is used for updating the last read notification time for a user
This is used to set the counter next to the notifications icon
"""


@bp.route("/reset_notifications", methods=["POST"])
@login_required
def reset_notifications():
    current_user.last_notification_read_time = datetime.utcnow()
    db.session.commit()
    return jsonify({"status": "reset"})


"""
This function describes the route for /deletefish
Permission required for this route are "Admin", "Owner"
This route is used for deleting an entry from the database
"""


@bp.route("/deletefish/<id>", methods=["POST"])
@login_required
@requires_roles("Admin", "Owner")
def deletefish(id):
    fish = Fish.query.filter_by(id=id).first()
    fish.delete_all_photos()
    db.session.delete(fish)
    db.session.commit()
    flash("The entry has been deleted", "info")
    return redirect(url_for("main.index"))


"""
This function describes the route for /deletereminder
Permission required for this route are "Researcher", "Admin", "Owner"
This route is used for deleting a reminder associated with a fish entry
"""


@bp.route("/deletereminder/<id>", methods=["POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def deletereminder(id):
    reminder = Reminder.query.filter_by(id=id).first()
    fish_id = reminder.fish.id
    db.session.delete(reminder)
    db.session.commit()

    flash("The reminder has been deleted", "info")
    return redirect(url_for("main.updatefish", id=fish_id))


"""
This function describes the route for /fish/deletephoto
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for deleting a fish associated with a fish entry
"""


@bp.route("/fish/<fish_id>/deletephoto/<photo_id>", methods=["POST"])
@login_required
@requires_roles("Researcher", "Admin", "Owner")
def deletephoto(fish_id, photo_id):
    fish = Fish.query.filter_by(id=fish_id).first_or_404()
    photo = Photo.query.filter_by(id=photo_id).first_or_404()
    photo.delete()

    flash("The picture has been deleted", "info")
    return redirect(url_for("main.fish", id=fish.id))


"""
This function describes the route for /deletedocument
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for deleting a document associated with a user
The document can be either personal or project license
"""


@bp.route("/deletedocument", methods=["POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def deletepersonallicense():

    jsdata = request.form["data"]

    if jsdata == "Personal":
        current_user.delete_personal_document()

    elif jsdata == "Project":
        current_user.delete_project_document()

    return jsdata


"""
This function describes the route for /deletenotifs
Permission required for this route are "User", "Researcher", "Admin", "Owner"
This route is used for clearing all of the notifications of a user
"""


@bp.route("/deletenotifs", methods=["POST"])
@login_required
@requires_roles("User", "Researcher", "Admin", "Owner")
def deletenotifs():
    notifications = current_user.notifications

    for notif in notifications:
        db.session.delete(notif)

    db.session.commit()
    return redirect(url_for("main.index"))


# This function is used to update the users Last seen time when they go to a new page
@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SimpleSearch()
        g.clearNotifsForm = EmptyForm()
