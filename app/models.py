# This is the main folder for the database
# This folder contains a class for each table in the database

from email.policy import default
from enum import unique
from math import remainder
import os
import re
import sys
from tracemalloc import start
from unicodedata import category

from sqlalchemy import delete, false
from app import db, bcrypt, login
from flask_login import UserMixin, current_user
from time import time
import jwt
from flask import current_app, abort
from datetime import datetime, timedelta
from functools import wraps
import json
from dateutil import relativedelta


"""
This is the class for the User table  of the SQL database
Each user is created as a new object of this class
This table has relationships to: Changes, Notification, Settings, Fish, Reminder
It also contains the methods required for the user
"""


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    project_license = db.Column(db.String(120))
    personal_license = db.Column(db.String(120))
    personal_document = db.Column(db.Boolean, default=False)
    project_document = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32), default="User")
    code = db.Column(db.String(32), index=True)
    changes = db.relationship("Change", backref="user", lazy="dynamic")

    notifications = db.relationship(
        "Notification", backref="user", lazy="dynamic", cascade="all, delete"
    )
    last_notification_read_time = db.Column(db.DateTime)

    reminders = db.relationship(
        "Reminder", backref="user", lazy="dynamic", cascade="all, delete"
    )

    def __repr__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def delete_personal_document(self):
        if not self.personal_document:
            return

        try:
            os.remove(
                os.path.join(current_app.config["PERSONAL_LICENSES"], f"{self.id}.pdf")
            )

        except:

            return

        self.personal_document = False
        db.session.commit()

    def delete_project_document(self):
        if not self.project_document:
            return

        try:
            os.remove(
                os.path.join(current_app.config["PROJECT_LICENSES"], f"{self.id}.pdf")
            )

        except:
            return

        self.project_document = False
        db.session.commit()

    def isOwner(self):
        return self.role == "Owner"

    def isAdmin(self):
        return self.role in ("Admin", "Owner")

    def isResearcher(self):
        return self.role in ("Researcher", "Admin", "Owner")

    # takes a password and returns its hash
    def set_password(self, password):
        # I implemented generate_password hash using the bcrypt hashing algorithm, uses bcrypt hash + salt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf8')

    # takes a password and a hash and checks if the match
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # this creates a secure signed payload using SHA256 to act as the verification for resetting a password it expires after 10 minutes
    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    # this works similar to above, but is used for email validation
    def get_email_verification_token(self, expires_in=600):
        return jwt.encode(
            {"verify_email": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    def new_notifications(self):
        last_read_time = self.last_notification_read_time or datetime(1900, 1, 1)
        return (
            Notification.query.filter_by(user=self)
            .filter(Notification.time > last_read_time)
            .count()
        )

    # this is used to verify a password reset token, it decodes the link and checks the id of the user exists
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["verify_email"]
        except:
            return
        return User.query.get(id)


# METHODS ASSOCIATED WITH USERS ---------------------------------------------
def get_all_user_codes():
    all_codes = User.query.with_entities(User.code).distinct()
    codes = [code[0] for code in all_codes]
    return sorted(filter(lambda x: x != None and x != "", codes))


def get_all_user_licenses():
    all_licenses = User.query.with_entities(User.project_license).distinct()
    licenses = [license[0] for license in all_licenses]
    return sorted(filter(lambda x: x != None and x != "", licenses))


# flask_login keeps track of logged in users, the users ID is loaded into memeory each time the load a new page
# flask_login doesn't know about the database so this function gives it the user ID
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# This method creates a wrapper, allowing the use of @required_roles in routes, allowing certain links to only be accessible for accounts with a certain role, e.g. admins


def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                # Redirect the user to an unauthorized notice!
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# --------------------------------


"""
This is the class for the Fish table of the SQL database
This is the main functionality of the system, each fish entry is stored as a new object of this class
This table has relationships to: Itself, User, Change, Notification, Allele, Photo, Reminder
It also contains the methods required for the fish
"""


class Fish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.String(264), index=True)
    tank_id = db.Column(db.String(32), index=True)
    status = db.Column(db.String(32), index=True, default="Alive")
    stock_name = db.Column(db.String(64), db.ForeignKey("stock.name"))
    source = db.Column(db.String(32))

    protocol = db.Column(db.Integer, index=True)
    birthday = db.Column(db.Date, index=True)
    date_of_arrival = db.Column(db.Date, index=True)
    months = db.Column(db.Integer, default=0)
    age_reminder = db.Column(db.String(64), default="Not sent")

    mutant_gene = db.Column(db.Text())
    cross_type = db.Column(db.String(64))
    comments = db.Column(db.Text())
    added = db.Column(db.DateTime, default=datetime.utcnow)

    father_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    mother_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    fathered = db.relationship(
        "Fish", backref=db.backref("father", remote_side=[id]), foreign_keys=[father_id]
    )
    mothered = db.relationship(
        "Fish", backref=db.backref("mother", remote_side=[id]), foreign_keys=[mother_id]
    )

    project_license_holder_id = db.Column(
        db.Integer, db.ForeignKey("user.id")
    )
    project_license_holder = db.relationship(
        "User", foreign_keys=[project_license_holder_id], backref="fish_on_license"
    )

    user_code_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_code = db.relationship(
        "User", foreign_keys=[user_code_id], backref="users_fish"
    )

    males = db.Column(db.Integer)
    females = db.Column(db.Integer)
    unsexed = db.Column(db.Integer)
    carriers = db.Column(db.Integer)
    total = db.Column(db.Integer)

    links = db.Column(db.Text())

    origin_tank_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    origin_for = db.relationship(
        "Fish",
        backref=db.backref("origin", remote_side=[id]),
        foreign_keys=[origin_tank_id],
    )

    changes = db.relationship(
        "Change", backref="fish", lazy="dynamic", cascade="all, delete"
    )

    notifications = db.relationship(
        "Notification", backref="fish", lazy="dynamic", cascade="all, delete"
    )

    reminders = db.relationship(
        "Reminder", backref="fish", lazy="dynamic", cascade="all, delete"
    )

    alleles = db.relationship(
        "Allele", backref="fish", lazy="dynamic", cascade="all, delete"
    )

    transgenes = db.relationship(
        "Transgene", backref="fish", lazy="dynamic", cascade="all, delete"
    )
    photos = db.relationship(
        "Photo", backref="fish", lazy="dynamic", cascade="all, delete"
    )

    # The following attributes are to make fish from the old system compatiable on the new database
    system = db.Column(db.String(64), default="New")
    old_code = db.Column(db.String(64))
    old_license = db.Column(db.String(64))
    old_mID = db.Column(db.Text())
    old_mStock = db.Column(db.String(64))
    old_fID = db.Column(db.Text())
    old_fStock = db.Column(db.String(64))
    old_birthday = db.Column(db.String(64))
    old_arrival = db.Column(db.String(64))
    old_allele = db.Column(db.Text())
    old_transgenes = db.Column(db.Text())


    def __repr__(self):
        return f"Stock: {self.stock_name}, Tank: {self.tank_id}, ID: {self.fish_id}"

    def get_ancestors(self, generation, relation=None):
        ancestors = []

        ancestors.append({"fish": self, "relation": relation, "level": generation})

        generation += 1

        if self.father is not None:
            ancestors = ancestors + self.father.get_ancestors(generation, "Father")
        if self.mother is not None:
            ancestors = ancestors + self.mother.get_ancestors(generation, "Mother")

        ancestors = sorted(ancestors, key=lambda x: x["level"])

        return ancestors

    def getAge(self):
        if self.old_birthday:
            self.birthday = datetime.strptime(self.old_birthday, "%Y-%m-%d").date()
            self.old_birthday = None
            db.session.commit()
            self.getAge()

        if self.status == "Dead":
            return "Dead"
        if self.birthday == None or self.birthday == "":
            return "None"

        today = datetime.today().date()
        birthday = self.birthday
        age_difference = relativedelta.relativedelta(today, birthday)

        if age_difference.years > 0:
            age = f"{age_difference.years} years, {age_difference.months} months, {age_difference.days} days"
        elif age_difference.months > 0:
            age = f"{age_difference.months} months, {age_difference.days} days"
        else:
            age = f"{age_difference.days} days"

        return age

    def setDateOfArrival(self):
        if self.date_of_arrival is not None:
            return

        if self.old_arrival is None or self.old_arrival == "":
            return

        self.date_of_arrival = datetime.strptime(self.old_arrival, "%Y-%m-%d").date()
        self.old_arrival = None
        db.session.commit()

    def getMonths(self):

        if self.status == "Dead":
            return 0
        try:
            today = datetime.today().date()
            birthday = self.birthday
            age_difference = relativedelta.relativedelta(today, birthday)

            return age_difference.months
        except:
            return 0
    def get_allele_names_string(self):
        if self.alleles is None:
            return " "
        name_list = [i.name for i in self.alleles]
        return "; ".join(name_list)

    def get_transgene_names_string(self):
        if self.transgenes is None:
            return " "
        name_list = [i.name for i in self.transgenes]
        return "; ".join(name_list)

    def delete_photo(self, photo_name):

        photo = Photo.query.filter_by(fish=self, name=photo_name).first()
        if photo != None:
            os.remove(os.path.join(current_app.config["FISH_PICTURES"], photo_name))

            db.session.delete(photo)
            db.session.commit()

    def delete_all_photos(self):
        photos = Photo.query.filter_by(fish=self).all()
        for photo in photos:

            os.remove(os.path.join(current_app.config["FISH_PICTURES"], photo.name))
            db.session.delete(photo)

        db.session.commit()

    def send_age_reminder(self, months):
        message = f"The tank is now {months} months old."
        if self.user_code is not None:
            reminder = Reminder(user=self.user_code, fish=self, message=message)
            db.session.add(reminder)
            self.age_reminder = f"{months} Months"
            db.session.commit()
            if self.project_license_holder is not None:
                reminder.send_reminder(
                    users=[self.project_license_holder.id], category="Age reminder"
                )
            else:
                reminder.send_reminder(category="Age reminder")
                
        elif self.project_license_holder is not None:
            reminder = Reminder(user=self.project_license_holder, fish=self, message=message)
            db.session.add(reminder)
            self.age_reminder = f"{months} Months"
            db.session.commit()
            reminder.send_reminder(category="Age reminder")



"""
This is the class for the Stock table of the SQL database
A stock can have multiple fish associated with it
This table has relationships to: Fish
"""
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    fish = db.relationship(
        "Fish", backref="stock", lazy="dynamic", cascade="all, delete"
    )
    current_total = db.Column(db.Integer)
    year_total = db.Column(db.Integer)
    fish_alive = db.Column(db.Boolean)
    culled = db.Column(db.Integer) 

    def __repr__(self):
        return self.name

    def get_culled_count(self):
        now = datetime.now()

        year = now.date().year
        year_dt = datetime(year, 1,1)
        culled = 0

        for fish in self.fish:
            #to get total at start of year
                #get tha last change in total before the date if there is one
                change_before = Change.query.filter_by(fish=fish, field = "total").filter(Change.time < year_dt ).order_by(Change.time.desc()).first()

                #get the first change in total after or on the date if there is one
                change_after = Change.query.filter_by(fish=fish, field = "total").filter(Change.time >= year_dt ).filter(Change.time <= now).order_by(Change.time.asc()).first()
                
                if change_before != None:
                    start_total = int(change_before.new)
                elif change_after != None:
                    start_total = int(change_after.old)
                else:
                    start_total = int(fish.total)

                culled += start_total - int(fish.total)

        self.culled = culled
        return culled

    def update_current_total(self):

        current = 0
        for fish in self.fish:
            current += fish.total

        self.current_total = current
        db.session.commit()

    def increase_yearly_total(self, num):
        if self.year_total is not None:
            self.year_total += num
        else:
            self.year_total = num

        db.session.commit()
    
    #this method is called on the first day of the year
    def update_yearly_total(self):

        self.update_current_total()

        self.year_total = int(self.current_total)

        db.session.commit()

    def has_alive_fish(self):
        for fish in self.fish:

            if fish.status != "Dead":
                self.fish_alive = True
                db.session.commit()
                return True

        self.fish_alive = False
        db.session.commit()
        return False
    def get_count_on_date(self, date):
        count = 0


        dt = datetime.combine(date, datetime.min.time())
        #for each fish associated with a stock
        for fish in self.fish:

            #if the fish was added after the date, ignore it
            if date < fish.added.date():
                continue

            #get the first change in total after or on the date if there is one
            change_after = Change.query.filter_by(fish=fish, field = "total").filter(Change.time >= dt).order_by(Change.time.asc()).first()

            #get tha last change in total before the date if there is one
            change_before = Change.query.filter_by(fish=fish, field = "total").filter(Change.time < dt).order_by(Change.time.desc()).first()

            #if there was a change after the date, take the old value from the closest change to the date
            if change_after is not None:
                count += int(change_after.old)

            #if there was only a change before the date, take the new value from the closest change to the date
            elif change_before is not None:
                count += int(change_before.new)

            #otherwise the total has never been changed so add the total to the count
            else:
                count += fish.total

        return count


"""
This is the class for the Allele table of the SQL database
A fish can have multiple alleles associated with it, each being a new object of this class
This table has relationships to: Fish
"""

class Allele(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    name = db.Column(db.String(128))
    unidentified = db.Column(db.Boolean, default=True)
    identified = db.Column(db.Boolean, default=False)
    homozygous = db.Column(db.Boolean, default=False)
    heterozygous = db.Column(db.Boolean, default=False)
    hemizygous = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Allele: {self.name} - Fish: {self.fish.stock_name}"


def get_all_allele_names():

    alleles = Allele.query.with_entities(Allele.name).distinct()
    names = set(allele[0] for allele in alleles)
    return names


"""
This is the class for the Transgene table of the SQL database
A fish can have multiple transgenes associated with it, each being a new object of this class
This table has relationships to: Fish
"""

class Transgene(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    name = db.Column(db.String(128))
    unidentified = db.Column(db.Boolean, default=True)
    identified = db.Column(db.Boolean, default=False)
    homozygous = db.Column(db.Boolean, default=False)
    heterozygous = db.Column(db.Boolean, default=False)
    hemizygous = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"Allele: {self.name} - Fish: {self.fish.stock_name}"

    
"""
This is the class for the Photo table of the SQL database
A fish can have multiple photos associated with it, each being a new object of this class
photos are stored as a string which contains the location of the photo within the app
This table has relationships to: Fish
"""


class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    name = db.Column(db.String(128))
    caption = db.Column(db.Text())

    def delete(self):
        os.remove(os.path.join(current_app.config["FISH_PICTURES"], self.name))
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"Photo - {self.name}"


"""
This is the class for the Change table of the SQL database, which is used to record changes to Fish objects the database
This table has relationships to: Fish, User, Notification
Users, Notifications and Fish can have many changes associated with them
"""


class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    action = db.Column(db.String(64))
    contents = db.Column(db.String(64))
    field = db.Column(db.String(64))
    old = db.Column(db.Text())
    new = db.Column(db.Text())
    time = db.Column(db.DateTime, default=datetime.utcnow)
    note = db.Column(db.Text())
    notification_id = db.Column(db.Integer, db.ForeignKey("notification.id"))

    def __repr__(self):
        return f"<Change by User:{self.user_id} on Fish: {self.fish_id}"


"""
This is the class for the Settings table of the SQL database
This table has a one-to-one relationships to User
"""


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # one-to-one relationship
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("settings", uselist=False))

    # this is emails for notifications
    emails = db.Column(db.Boolean, default=False)

    email_reminders = db.Column(db.Boolean, default=False)
    pl_email_reminders = db.Column(db.Boolean, default=False)

    add_notifications = db.Column(db.Boolean, default=True)
    change_notifications = db.Column(db.Boolean, default=True)
    custom_reminder = db.Column(db.Boolean, default=True)
    age_notifications = db.Column(db.Boolean, default=True)

    pl_add_notifications = db.Column(db.Boolean, default=False)
    pl_custom_reminder = db.Column(db.Boolean, default=True)
    pl_age_notifications = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Settings for User:{self.user.username}"


"""
This is the class for the Notifiaction table of the SQL database
This table has relationships to: User, Fish, Change
Users and Fish can have many notifications
Notifications can related to multiple changes
It also contains the methods required for the notifiaction
"""


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))

    time = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(64))
    contents = db.Column(db.String(64))
    change_count = db.Column(db.Integer)
    changes = db.relationship(
        "Change", backref="notification", lazy="dynamic", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Notification for User:{self.user.username}>"

    def send_email(self):
        if self.user == None:
            return
        if self.user.settings.emails:
            from app.main.emails import send_notification_email

            send_notification_email(self.user, self)


"""
This is the class for the Reminder table of the SQL database
This table has relationships to: Fish, User
Users and Fish can have many reminders associated with them
"""


class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    date = db.Column(db.Date)
    message = db.Column(db.String(64))
    sent = db.Column(db.Boolean, default=False)

    # send notification from reminder, can take more than one user
    def send_reminder(self, users=[], category="Reminder"):

        from app.main.emails import send_reminder_email

        users.append(self.user.id)

        for user in users:
            user_done = False
            user = User.query.filter_by(id=user).first()
            if user is None:
                continue

            if category == "Reminder":
                if self.fish.user_code is not None:
                    if user.settings.custom_reminder and  user == self.fish.user_code:
                        notification = Notification(
                            user=user,
                            fish=self.fish,
                            category="Reminder",
                            contents=self.message,
                        )
                        db.session.add(notification)

                        if user.settings.email_reminders:
                            send_reminder_email(user, self)

                        user_done = True

                if user_done != True and self.fish.project_license_holder is not None:
                    if user.settings.pl_custom_reminder and  user == self.fish.project_license_holder:
                        notification = Notification(
                            user=user,
                            fish=self.fish,
                            category="Reminder",
                            contents=self.message,
                        )
                        db.session.add(notification)

                        if user.settings.pl_email_reminders :
                            send_reminder_email(user, self)

            elif category == "Age reminder": 
                if self.fish.user_code is not None:
                    if user.settings.age_notifications and  user == self.fish.user_code:
                        notification = Notification(
                            user=user,
                            fish=self.fish,
                            category="Reminder",
                            contents=self.message,
                        )
                        db.session.add(notification)

                    if user.settings.email_reminders:
                        send_reminder_email(user, self)
                    
                    user_done = True

                if user_done != True and self.fish.project_license_holder is not None:
                    if user.settings.pl_age_notifications and  user == self.fish.project_license_holder:
                        notification = Notification(
                            user=user,
                            fish=self.fish,
                            category="Reminder",
                            contents=self.message,
                        )
                        db.session.add(notification)

                    if user.settings.pl_email_reminders:
                        send_reminder_email(user, self)

            

            

        self.sent = True
        db.session.commit()

    def __repr__(self):

        return (
            f"Reminder - User:{self.user} Messgae: {self.message}, Date: {self.date}, Sent: {self.sent}"
        )
