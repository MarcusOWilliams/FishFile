
from flask import render_template, current_app
from app.email import send_email

#this takes a user, generates a secure password token and sends an email to them to reset their password
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(('[DanioDB] Reset Your Password'),
               sender=current_app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/reset_password_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password_email.html',
                                         user=user, token=token))

#
def send_email_verification_email(user):
    token = user.get_email_verification_token()
    send_email(('[DanioDB] Verify Your Email'),
               sender=current_app.config['MAIL_DEFAULT_SENDER'],
               recipients=[user.email],
               text_body=render_template('email/verify_email_email.txt',
                                         user=user, token=token),
               html_body=render_template('email/verify_email_email.html',
                                         user=user, token=token))

def send_enquiry_email(name, user, enquiry):
    send_email(
        (f'[USER ENQUIRY] - {name}'),
        sender=current_app.config['ADMINS'][0],
        recipients=current_app.config['ADMINS'][0],
        text_body=render_template('email/enquiry_email.txt', name=name, user_email=user, enquiry=enquiry),
        html_body=render_template('email/enquiry_email.html', name=name, user_email=user, enquiry=enquiry)
        )