# Used the help of ChatGPT's code to implement the scheduler

from apscheduler.schedulers.background import BackgroundScheduler
from models.meeting import Meeting
from models.task_progress import TaskProgress
from datetime import datetime, timedelta
from app import db


def check_meeting_reminders(app):
    with app.app_context():
        now = datetime.utcnow()
        meetings = Meeting.query.filter(Meeting.date_time > now).all()
        for meeting in meetings:
            meeting.check_reminders()


def check_task_due_date(app):
    with app.app_context():
        tasks =TaskProgress.query.filter(TaskProgress.status == "Pending").all()
        for task in tasks:
            task.check_due_date(task.assigned_to)

def delete_old_meeting(app):
    with app.app_context():
        now = datetime.utcnow()
        meetings = Meeting.query.filter(Meeting.date_time < (now + timedelta(hours=2))).all()
        for meeting in meetings:
            Meeting.query.filter_by(id=meeting.id).delete()
            db.session.commit()


# Scheduler initialization function
def initialize_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_meeting_reminders, 'interval', minutes=300, args=[app]) # Check every 5 hours
    scheduler.add_job(check_task_due_date, 'interval', minutes=300, args=[app]) # Check every 5 hours
    scheduler.add_job(delete_old_meeting, 'interval', minutes=120, args=[app]) # Check every 2 hours
    scheduler.start()
    print("Scheduler started successfully.")
