"""
This module is associated speciically with sending any emails involved in the main blueprint
This includes the notification email
This module uses methods from app/emails.py to send the email
"""
from flask import render_template, current_app
from app.email import send_email
from app.models import *

#This email take a user and a notification sends an email notification to the user 
def send_notification_email(user, notification):
    if not user.settings.emails:
        return

    send_email(
        ("[DanioDB] Notification"),
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template(
            "email/notification.txt", user=user, notification=notification
        ),
        html_body=render_template(
            "email/notification.html", user=user, notification=notification
        ),
    )

#This email take a user and a notification sends an email notification to the user 
def send_reminder_email(user, reminder):
    
    if not user.settings.email_reminders:
        return

    send_email(
        ("[DanioDB] Reminder"),
        sender=current_app.config["MAIL_DEFAULT_SENDER"],
        recipients=[user.email],
        text_body=render_template(
            "email/reminder.txt", user=user, reminder=reminder
        ),
        html_body=render_template(
            "email/reminder.html", user=user, reminder=reminder
        ),
    )
