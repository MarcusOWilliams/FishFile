from flask import render_template, current_app
from app.email import send_email
from app.models import *


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
