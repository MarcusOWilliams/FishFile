from app import scheduler, db
import sys
from app.models import Fish, Notification
from datetime import datetime

@scheduler.task('cron', id='do_job_1',hour='4')
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


    