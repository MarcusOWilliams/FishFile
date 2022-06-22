# This is the main folder for the database
# This folder contains a class for each table in the database

from app import db, bcrypt, login
from flask_login import UserMixin, current_user
from time import time
import jwt
from flask import current_app, abort
from datetime import datetime
from functools import wraps


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    username = db.Column(db.String(64), index=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(64), default='User')
    changes = db.relationship('Change', backref='user', lazy='dynamic')
    notification = db.relationship('Notification', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {} {}>'.format(self.first_name, self.last_name)

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
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    # this works similar to above, but is used for email validation
    def get_email_verification_token(self, expires_in=300):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    # this is used to verify a password reset token, it decodes the link and checks the id of the user exists
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    @staticmethod
    def verify_email_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['verify_email']
        except:
            return
        return User.query.get(id)


# METHODS ASSOCIATED WITH USERS ---------------------------------------------

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


class Fish(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fish_id = db.Column(db.String(64), index=True, unique=True)
    birthday = db.Column(db.Date, index=True)
    date_of_arrival = db.Column(db.Date, index=True)
    stock = db.Column(db.String(64), index=True)
    project_license = db.Column(db.String(64), index=True)
    status = db.Column(db.String(64), index=True, default = "Alive")
    allele = db.Column(db.String(64), index=True)
    sex = db.Column(db.String(64))
    mutant_gene = db.Column(db.String(64), index=True)
    transgenes = db.Column(db.String(64), index=True)
    protocol = db.Column(db.Integer, index=True)
    comments = db.Column(db.String(1000))

    father_id = db.Column(db.Integer, db.ForeignKey('fish.id'))
    mother_id = db.Column(db.Integer, db.ForeignKey('fish.id'))
    fathered = db.relationship("Fish", backref=db.backref("father", remote_side=[id]), foreign_keys = [father_id])
    mothered = db.relationship("Fish", backref=db.backref("mother", remote_side=[id]), foreign_keys= [mother_id])

    changes = db.relationship("Change", backref='fish', lazy='dynamic')

    tank_id =  db.Column(db.Integer, db.ForeignKey('tank.id'))

    def __repr__(self):
        return f'<Fish: id = {self.fish_id}>'
    

class Tank(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tank_id = db.Column(db.String(64), index=True, unique=True)
    males = db.Column(db.Integer)
    females = db.Column(db.Integer)
    unsexed = db.Column(db.Integer)
    carriers = db.Column(db.Integer)
    total = db.Column(db.Integer)

    fish = db.relationship("Fish", backref = "tank", lazy='dynamic')

class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    fish_id = db.Column(db.Integer, db.ForeignKey('fish.id'))
    tank_id =  db.Column(db.Integer, db.ForeignKey('tank.id'))
    action = db.Column(db.String(64))
    contents = db.Column(db.String(64))
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Change by User:{self.user_id} on Fish: {self.fish_id}'

class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #one-to-one relationship
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref = db.backref("settings", uselist=False))

    emails = db.Column(db.Boolean, default = True)

    def __repr__(self):
        return f'<Settings for User:{self.user.username}'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    category = db.Column(db.String(64))
    contents = db.Column(db.String(64))

    def __repr__(self):
        return f'<Notification for User:{self.user.username}'



