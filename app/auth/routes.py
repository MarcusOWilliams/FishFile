from app import db
from app.auth import bp
from flask import render_template, redirect, url_for, flash, request
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from werkzeug.urls import url_parse
from app.auth.email import send_password_reset_email
import os

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        
        user = User.query.filter_by(email=form.email.data).first()

        #check if they have entered an email that is in the db
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        
        #once the user is loged in they are redirected to the page they tried to visit, if they came straight to the login page they are just redirected to the home page
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')

        return redirect(next_page)
       
    return render_template('auth/login.html', title='Sign In', form=form)

#If the user logs out they are simply directed to this url, logged out, then returned to the index page
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

#The url for account registration
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(first_name = form.first_name.data, last_name = form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', title='Register', form=form)   

#this url is for someone to request a reset of their password by submiting their email
# If there is an account associated with the email they will recieve a password reset email    
@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Check your email for the instructions to reset your password')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html',title='Reset Password', form=form)

#this is the url which is visted to set the new password, it takes the token (from an email), checks it then allows password reset
@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('The password reset link you used was either invalid or has expired.')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
