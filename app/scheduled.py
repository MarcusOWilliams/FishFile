#This file does the same as tasks.py, but is used by teh pythonanywhere scheduled tasks rather than apschedular
from datetime import datetime

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


from app import db, create_app
from app.models import Fish, Notification, Reminder, Stock

app = create_app()

def delete_old_notifications():
    with app.app_context():
        notifications = Notification.query.all()
        for notif in notifications:
            # how old is the notification in days
            notif_age = (datetime.today() - notif.time).days

            # if the notification is more than 100 dyas old, delete the notification
            if notif_age > 100:
                db.session.delete(notif)

        #commit the changes to the database
        db.session.commit()
    print("old notifs deleted ", str(datetime.now()))


def send_reminders():
    with app.app_context():
        reminders = Reminder.query.all()
        for reminder in reminders:
            if reminder.sent:
                continue
            if reminder.date is not None:
                if reminder.date <= datetime.today().date():
                    reminder.send_reminder()
        print("reminders sent ", str(datetime.now()))

def update_fish_months():
    with app.app_context():
        all_fish = Fish.query.filter(
            Fish.status != "Dead", Fish.birthday != None, Fish.system != "Old"
        ).all()

        for fish in all_fish:

            fish.months = fish.getMonths()



        db.session.commit()
        print("months updated "+str(datetime.now()))

def send_age_reminders():
    with app.app_context():
        all_fish = Fish.query.filter(Fish.status != "Dead", Fish.system != "Old").all()
        for fish in all_fish:

            if fish.months >= 23 and fish.age_reminder != "23 Months":
                fish.send_age_reminder(23)

            elif fish.months >= 17 and fish.age_reminder != "17 Months":
                fish.send_age_reminder(17)

            elif fish.months >= 11 and fish.age_reminder != "11 Months":
                fish.send_age_reminder(11)

            elif fish.months >= 5 and fish.age_reminder != "5 Months":
                fish.send_age_reminder(5)
        print("age reminders sent "+str(datetime.now()))





def update_stock_yearly():
    with app.app_context():
        today = datetime.today()
        if int(today.month) == 8 and int(today.day) == 18:
            stocks = Stock.query.all()
            for stock in stocks:
                if len(list(stock.fish)) < 1:
                    db.session.delete(stock)
                stock.update_yearly_total()

            print("yearly update "+str(datetime.now()))

delete_old_notifications()
send_reminders()
update_fish_months()
send_age_reminders()
update_stock_yearly()
print("all done")