from msilib.schema import Error
from app import db
from app.auth import bp
from app.auth.email import send_email_verification_email, send_password_reset_email
from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
    ChangePasswordForm,
)
from app.models import Settings, User
from flask import flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.urls import url_parse


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()
        
        # check if they have entered an email that is in the db
        if user is None or not user.check_password(form.password.data):
            flash("Invalid email or password", "danger")
            return redirect(url_for("auth.login"))

        #If the user's role has been set to blocked, deny login
        if user.role =="Blocked":
            flash(f"This account has been removed, if you think this is a mistake please contact your system manager to resolve the issue.", "danger")
            return redirect(url_for("auth.login"))

        # if the user is not verified they are sent a verification email
        if not user.is_verified:
            send_email_verification_email(user)
            flash(
                f"To login you must verify your email address, a verification link has been sent to {user.email}, don't forget to check your spam folder!",
                "info",
            )
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)

        # once the user is logged in and verified they are redirected to the page they tried to visit, if they came straight to the login page they are just redirected to the home page
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")

        return redirect(next_page)

    return render_template("auth/login.html", title="Sign In", form=form)


# If the user logs out they are simply directed to this url, logged out, then returned to the index page
@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.landing"))


# The url for account registration
@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()

    if form.validate_on_submit():

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        user.username = user.email.split("@")[0]
        db.session.add(user)

        

        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", title="Register", form=form)


# this url is for someone to request a reset of their password by submiting their email
# If there is an account associated with the email they will recieve a password reset email
@bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            "If there is an email associated with the an account an email will be sent with instructions on how to reset your password, please check your junk/spam folder!",
            "info",
        )
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html", title="Reset Password", form=form
    )


# this is the url which is visted to set the new password, it takes the token (from an email), checks it then allows password reset
@bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        flash(
            "The password reset link you used was either invalid or has expired.",
            "danger",
        )
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)

"""
This function describes the route for /verify_email
This route is used for verifying the email of a user, given a token
"""
@bp.route("/verify_email/<token>", methods=["GET"])
def verify_email(token):
    user = User.verify_email_token(token)
    if not user:
        flash(
            "The email verification link you used was either invalid or has expired.",
            "danger",
        )
        return redirect(url_for("auth.login"))
    user.is_verified = True

    #create user code on account verification, this avoids unverified accounts having codes which clog up the select options
    user.code = f"{user.first_name[0]}{user.last_name[0]} ({user.username})"
    
    db.session.commit()
    flash("Your email has been verified", "success")
    return redirect(url_for("auth.login"))

"""
This function describes the route for /change_password
This route is used for updating the password for a user
"""
@bp.route("/change_password/", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash(
                "The current password you entered is incorrect. If you have forgotten your password, logout and use the 'forgoten password' link on the login page.",
                "danger"
            )
            return redirect(url_for("auth.change_password"))

        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password has been changed.", "success")
        return redirect(url_for("main.settings"))

    return render_template(
        "auth/change_password.html", title="Change Password", form=form
    )
