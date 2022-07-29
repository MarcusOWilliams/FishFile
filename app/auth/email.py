"""
This module is associated with sending any emails involved in the auth blueprint
This includes, email verification and password resets
This module uses methods from app/emails.py to send the email
"""
from flask import render_template, current_app
from app.email import send_email

# this takes a user, generates a secure password token and sends an email to them to reset their password
# The methods for getting and verifying the tokens are in the User class of app/models.py
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        (f'[{current_app.config["WEBSITE_NAME"]}] Reset Your Password'),
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template(
            "email/reset_password_email.txt", user=user, token=token
        ),
        html_body=render_template(
            "email/reset_password_email.html", user=user, token=token
        ),
    )


# this takes a user, generates a secure verification token and sends an email to them to reset their password
# The methods for getting and verifying the tokens are in the User class of app/models.py
def send_email_verification_email(user):
    token = user.get_email_verification_token()
    send_email(
        (f'[{current_app.config["WEBSITE_NAME"]}] Verify Your Email'),
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template(
            "email/verify_email_email.txt", user=user, token=token
        ),
        html_body=render_template(
            "email/verify_email_email.html", user=user, token=token
        ),
    )
