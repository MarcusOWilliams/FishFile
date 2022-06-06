#This is the main folder for the database
#This folder contains a class for each table in the database

from app import db, bcrypt, login
from flask_login import UserMixin
from time import time
import jwt
from flask import current_app
from datetime import datetime



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_verified = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<User {}>'.format(self.username)

    #takes a password and returns its hash
    def set_password(self, password):
        #I implemented generate_password hash using the bcrypt hashing algorithm, uses bcrypt hash + salt
        self.password_hash = bcrypt.generate_password_hash(password)

    #takes a password and a hash and checks if the match
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    #this creates a secure signed payload using SHA256 to act as the verification for resetting a password it expires after 5 minutes
    def get_reset_password_token(self, expires_in=300):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    #this works similar to above, but is used for email validation
    def get_email_verification_token(self, expires_in=300):
        return jwt.encode(
            {'verify_email': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')


    #this is used to verify a password reset token, it decodes the link and checks the id of the user exists
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


#flask_login keeps track of logged in users, the users ID is loaded into memeory each time the load a new page
#flask_login doesn't know about the database so this function gives it the user ID
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
