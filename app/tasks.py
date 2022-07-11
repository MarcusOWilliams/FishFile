from app import scheduler
import sys
from app.models import Fish

@scheduler.task('cron', id='do_job_1',hour='6')
def job1():
    with scheduler.app.app_context():
        fish = Fish.query.all()
        for f in fish:
            print(f, file = sys.stderr)
        print('Job 1 executed', file=sys.stderr)


    