from app import scheduler, db
import sys
from app.models import Fish, Notification, Reminder
from datetime import datetime
from dateutil import relativedelta


@scheduler.task("cron", id="clear_old_notifs", hour="4")
def delete_old_notifications():
    with scheduler.app.app_context():
        notifications = Notification.query.all()
        for notif in notifications:
            # how old is the notification in days
            notif_age = (datetime.today() - notif.time).days

            # if the notification is more than 100 dyas old, delete the notification
            if notif_age > 100:
                db.session.delete(notif)

        db.session.commit()


@scheduler.task("cron", id="send_reminders", hour="5")
def send_reminders():
    with scheduler.app.app_context():
        reminders = Reminder.query.all()
        for reminder in reminders:
            if reminder.sent:
                continue
            if reminder.date <= datetime.today().date():
                reminder.send_reminder()


@scheduler.task("cron", id="send_age_reminders", hour="2")
def send_age_reminders():
    with scheduler.app.app_context():
        all_fish = Fish.query.filter(Fish.status != "Dead", Fish.system != "Old").all()
        for fish in all_fish:

            if fish.getMonths() >= 23 and fish.age_reminder != "23 Months":
                fish.send_age_reminder(23)

            elif fish.getMonths() >= 17 and fish.age_reminder != "17 Months":
                fish.send_age_reminder(17)

            elif fish.getMonths() >= 11 and fish.age_reminder != "11 Months":
                fish.send_age_reminder(11)

            elif fish.getMonths() >= 5 and fish.age_reminder != "5 Months":
                fish.send_age_reminder(5)
        print("task done")


@scheduler.task("cron", id="update_fish_months", hour="1")
def update_fish_months():
    with scheduler.app.app_context():
        all_fish = Fish.query.filter(
            Fish.status != "Dead", Fish.birthday != None, Fish.system != "Old"
        ).all()

        for fish in all_fish:

            fish.months = fish.getMonths()
            print(f"{fish} updated")

        db.session.commit()
