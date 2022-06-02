from app import db
from app.auth import bp
from flask import render_template, redirect, url_for, flash, request
from app.auth.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user
from app.models import User
from werkzeug.urls import url_parse

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
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


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        mainUsername =  os.environ.get('MAIN_ACCOUNT')
        mainUser = User.query.filter_by(username=mainUsername).first()
        if mainUser:
            user.follow(mainUser)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)   