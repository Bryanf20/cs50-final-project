from datetime import datetime
from . import db
from models.group import Group
from models.notification import Notification

class TaskProgress(db.Model):
    __tablename__ = 'task_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    task_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Options: Pending, Completed
    due_date = db.Column(db.DateTime, nullable=True)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    group = db.relationship('Group', backref=db.backref('tasks', lazy=True))
    assigned_user = db.relationship('User', backref='tasks')

    def __repr__(self):
        return f"<TaskProgress {self.task_name} - {self.status}>"
    
    # Check for due date
    def check_due_date(self, user_id=None):
        time_difference = self.due_date - datetime.utcnow()
        total_days = time_difference.total_seconds() / 86400  # Convert seconds to days
        days_remaining = int(total_days)
        message = None

        if days_remaining >= 0 and days_remaining <= 2:
            # Task is about to be due
            message = f'Task "{self.task_name}" is due in {days_remaining} day(s).'
        elif days_remaining < 0:
            # Task is overdue
            overdue_days = abs(days_remaining)
            message = f'Task "{self.task_name}" is overdue by {overdue_days} day(s).'

        if message:
            if user_id:
                # Notify a specific user
                existing_notification = Notification.query.filter_by(
                    user_id=user_id,
                    message=message,
                    is_read=False
                ).first()

                if not existing_notification:
                    self.create_notification(user_id, message, due_date=self.due_date)
            else:
                # Notify all group members for unassigned tasks
                self.notify_group_members(message)


    def create_notification(self, user_id, message, due_date):
        notification = Notification(user_id=user_id, message=message, due_date=due_date)
        db.session.add(notification)
        db.session.commit()


    def notify_group_members(self, message):
        group = Group.query.get(self.group_id)
        if group is None:
            # Handle the error or return a message indicating group is not found
            print("Group not found! Deleting the task.")
            db.session.delete(self)
            db.session.commit()
            return

        for user in group.members:
            existing_notification = Notification.query.filter_by(
                user_id=user.id,
                message=message,
                is_read=False
            ).first()

            if not existing_notification:
                notification = Notification(user_id=user.id, message=message, due_date=self.due_date)
                db.session.add(notification)

        db.session.commit()
