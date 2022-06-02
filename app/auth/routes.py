from app.auth import bp
from flask import render_template, redirect, url_for, flash
from app.auth.forms import LoginForm
from flask_login import current_user, login_user, logout_user
from app.models import User

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter(username = form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
       
    return render_template('auth/login.html', title='Sign In', form=form)

#If the user logs out they are simply directed to this url, logged out, then returned to the index page
@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))