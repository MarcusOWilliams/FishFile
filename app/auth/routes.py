from app.auth import bp
from flask import render_template, flash, redirect
from app.auth.forms import LoginForm

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect('/')
    return render_template('auth/login.html', title='Sign In', form=form)