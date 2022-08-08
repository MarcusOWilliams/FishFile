from app.tasks import *


def test_tasks(test_client):
    try:
        send_age_reminders()
        delete_old_notifications()
        send_reminders()
        update_fish_months()
        update_stock_yearly()
    except:
        raise AssertionError("Tasks not functioning correctly")


