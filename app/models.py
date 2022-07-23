# This is the main folder for the database
# This folder contains a class for each table in the database

from email.policy import default
from math import remainder
import os
import sys
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
Each user row contains a unique id, names, email, username, hashed_password, last seen time, verification check, role 
This table has relationships to: Changes, Notification, Settings, Fish
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

    notifications = db.relationship("Notification", backref="user", lazy="dynamic", cascade="all, delete")
    last_notification_read_time = db.Column(db.DateTime)

    reminders = db.relationship(
        "Reminder", backref="user", lazy="dynamic", cascade="all, delete"
    )

    def __repr__(self):
        return "<User {} {}>".format(self.first_name, self.last_name)
    
    def delete_personal_document(self):
        if not self.personal_document:
            return

        try:
            os.remove(os.path.join(current_app.config['PERSONAL_LICENSES'], f"{self.id}.pdf"))

        except:

            return
            

        self.personal_document = False
        db.session.commit()

    def delete_project_document(self):
        if not self.project_document:
            return

        try:
            os.remove(os.path.join(current_app.config['PROJECT_LICENSES'], f"{self.id}.pdf"))
            
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
        self.password_hash = bcrypt.generate_password_hash(password)

    # takes a password and a hash and checks if the match
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    # this creates a secure signed payload using SHA256 to act as the verification for resetting a password it expires after 5 minutes
    def get_reset_password_token(self, expires_in=300):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    # this works similar to above, but is used for email validation
    def get_email_verification_token(self, expires_in=300):
        return jwt.encode(
            {"verify_email": self.id, "exp": time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    def new_notifications(self):
        last_read_time = self.last_notification_read_time or datetime(1900, 1, 1)
        return Notification.query.filter_by(user=self).filter(Notification.time > last_read_time).count()
    
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
    return sorted(filter(lambda x: x!= None and x!="", codes))

def get_all_user_licenses():
    all_licenses = User.query.with_entities(User.project_license).distinct()
    licenses = [license[0] for license in all_licenses]
    return sorted(filter(lambda x: x!= None and x!="", licenses))
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
            if current_app.testing == True:
                return f(*args, **kwargs)

            if current_user.role not in roles:
                # Redirect the user to an unauthorized notice!
                abort(403)
            return f(*args, **kwargs)

        return wrapped

    return wrapper


# --------------------------------


"""
This is the class for the Fish table of the SQL database
Each user row contains a ...
This table has relationships to: Itself, User, Change, Tank
It also contains the methods required for the fish
"""


class Fish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.String(264), index=True)
    tank_id = db.Column(db.String(32), index=True)
    status = db.Column(db.String(32), index=True, default="Alive")
    stock = db.Column(db.String(32), index=True)
    source = db.Column(db.String(32))

    protocol = db.Column(db.Integer, index=True)
    birthday = db.Column(db.Date, index=True)
    date_of_arrival = db.Column(db.Date, index=True)
    months = db.Column(db.Integer, default = 0)
    age_reminder = db.Column(db.String(64), default = "Not sent")

    mutant_gene = db.Column(db.Text())
    transgenes = db.Column(db.Text())
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
        db.Integer, db.ForeignKey("user.project_license")
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
        "Fish", backref=db.backref("origin", remote_side=[id]), foreign_keys=[origin_tank_id]
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
    photos = db.relationship(
        "Photo", backref="fish", lazy="dynamic", cascade="all, delete"
    ) 

    #The following attributes are to make fish from the old system compatiable on the new database
    system = db.Column(db.String(64), default = "New")
    old_code = db.Column(db.String(64))
    old_license = db.Column(db.String(64))
    old_mID = db.Column(db.String(64))
    old_mStock = db.Column(db.String(64))
    old_fID = db.Column(db.String(64))
    old_fStock = db.Column(db.String(64))
    old_birthday = db.Column(db.String(64))
    old_arrival = db.Column(db.String(64))
    old_allele = db.Column(db.String(64))



    def __repr__(self):
        return f"ID: {self.fish_id}, Stock: {self.stock}, Tank: {self.tank_id}"

    def get_ancestors(self,generation, relation = None):
        ancestors = []
        
        ancestors.append({"fish":self,"relation":relation,"level" : generation})

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
            self.old_birthday=None
            db.session.commit()
            self.getAge()
            
        if self.status == "Dead":
            return "Dead"
        if self.birthday == None or self.birthday=="":
            return "None"

        today = datetime.today().date()
        birthday =  self.birthday
        age_difference = relativedelta.relativedelta(today,birthday)

        if age_difference.years>0:
            age = f"{age_difference.years} years, {age_difference.months} months, {age_difference.days} days"
        elif age_difference.months>0:
            age = f"{age_difference.months} months, {age_difference.days} days"
        else:
            age = f"{age_difference.days} days"

        return age
        
    def getMonths(self):

        if self.status == "Dead":
            return 0
        try:
            today = datetime.today().date()
            birthday =  self.birthday
            age_difference = relativedelta.relativedelta(today,birthday)
            
            return age_difference.months
        except:
            return 0
        
    def delete_photo(self, photo_name):
        
        photo = Photo.query.filter_by(fish = self, name = photo_name).first()
        if photo != None:
            os.remove(os.path.join(current_app.config['FISH_PICTURES'], photo_name))

            db.session.delete(photo)
            db.session.commit()
            


    def delete_all_photos(self):
        photos = Photo.query.filter_by(fish = self).all()
        for photo in photos:

            os.remove(os.path.join(current_app.config['FISH_PICTURES'],photo.name))
            db.session.delete(photo)

        db.session.commit()
    
    def send_age_reminder(self, months):
        message = f"The tank is now {months} months old."
        reminder = Reminder(user = self.user_code, fish=self, message=message)
        db.session.add(reminder)
        self.age_reminder = f"{months} Months"
        db.session.commit()
        reminder.send_reminder(users = [self.project_license_holder.id], category="Age reminder")


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
        return f"Allele: {self.name} - Fish: {self.fish.stock}"

def get_all_allele_names():
    
    alleles = Allele.query.with_entities(Allele.name).distinct()
    names = set(allele[0] for allele in alleles)
    return names
    
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    name = db.Column(db.String(128))
    caption = db.Column(db.Text())

    def delete(self):
        os.remove(os.path.join(current_app.config['FISH_PICTURES'],self.name))
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f"Photo - {self.name}"
"""
This is the class for the Change table of the SQL database, which is used to record changes to the database
Each user row contains a ...
This table has relationships to: Fish, User, Tank
It also contains the methods required for the change
"""


class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    action = db.Column(db.String(64))
    contents = db.Column(db.String(64))
    field = db.Column(db.String(64))
    old = db.Column(db.String(64))
    new = db.Column(db.String(64))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    notification_id = db.Column(db.Integer, db.ForeignKey("notification.id"))



    def __repr__(self):
        return f"<Change by User:{self.user_id} on Fish: {self.fish_id}"


"""
This is the class for the Setting table of the SQL database
Each user row contains a ...
This table has a one-to-one relationships to User
It also contains the methods required for the Settings
"""


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # one-to-one relationship
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref=db.backref("settings", uselist=False))

    #this is emails for notifications
    emails = db.Column(db.Boolean, default=False)

    email_reminders = db.Column(db.Boolean, default=False)
    
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
Each user row contains a ...
This table has relationships to: User
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
    changes =  db.relationship(
        "Change", backref="notification", lazy="dynamic", cascade="all, delete"
    )

    def __repr__(self):
        return f"<Notification for User:{self.user.username}>"

    def send_email(self):
        if self.user == None:
            return
        if self.user.settings.emails:
            from app.main.email import send_notification_email
            send_notification_email(self.user, self)
 

class Reminder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    fish_id = db.Column(db.Integer, db.ForeignKey("fish.id"))
    date = db.Column(db.Date)
    message = db.Column(db.String(64))
    sent = db.Column(db.Boolean, default= False)

    #send notification from reminder, can take more than one user
    def send_reminder(self, users = [], category="Reminder"):

       
        from app.main.email import send_reminder_email

        users.append(self.user_id)

        for user in users:
            user = User.query.filter_by(id=user).first()
            if user is None:
                continue

            
            if category == "Reminder" and (user.settings.custom_reminder or user.settings.pl_custom_reminder):

                notification = Notification(user = user, fish = self.fish, category="Reminder", contents = self.message)
                db.session.add(notification)
            elif category == "Age reminder" and (user.settings.age_notifications or user.settings.pl_age_notifications) :
                notification = Notification(user = user, fish = self.fish, category="Reminder", contents = self.message)
                db.session.add(notification)

        



            if user.settings.email_reminders:
                send_reminder_email(user, self)

        self.sent=True
        db.session.commit()




