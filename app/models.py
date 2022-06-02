#This is the main folder for the database
#This folder contains a class for each table in the database

from app import db, bcrypt, login
from flask_login import UserMixin



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    #takes a password and returns its hash
    def set_password(self, password):
        #I implemented generate_password hash using the bcrypt hashing algorithm, uses bcrypt hash + salt
        self.password_hash = bcrypt.generate_password_hash(password)

    #takes a password and a hash and checks if the match
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


#flask_login keeps track of logged in users, the users ID is loaded into memeory each time the load a new page
#flask_login doesn't know about the database so this function gives it the user ID
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
