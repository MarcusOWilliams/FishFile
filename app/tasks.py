from app import scheduler, db
import sys
from app.models import Fish, Notification, Reminder
from datetime import datetime
from dateutil import relativedelta

@scheduler.task('cron', id='clear_old_notifs',hour='4')
def delete_old_notifications():
    with scheduler.app.app_context():
        notifications = Notification.query.all()
        for notif in notifications:
            #how old is the notification in days
            notif_age = (datetime.today()-notif.time).days
            
            #if the notification is more than 100 dyas old, delete the notification
            if notif_age>100:
                db.session.delete(notif)
        

        db.session.commit()


@scheduler.task('cron', id='send_reminders',hour='5')
def send_reminders():
    with scheduler.app.app_context():
        reminders = Reminder.query.all()
        for reminder in reminders:
            if reminder.sent:
                continue
            if reminder.date <= datetime.today().date():
                reminder.send_reminder()


        


    