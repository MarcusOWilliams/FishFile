from threading import Thread
from flask_mail import Message
from app import mail
from flask import current_app

#This is where the main email methods are kept
#these are used in other parts of the app to send email, for example password reset

#this is used by the send email function below to send the emails asynchronously to avoid slowing other tasks
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


#This is the main method that prepares the email and then sends it using the method above
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
