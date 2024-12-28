from datetime import datetime
from . import db
from models.group import Group
from models.notification import Notification

class TaskProgress(db.Model):
    __tablename__ = 'task_progress'

    id = db.Column(db.Integer, primary_key=True)
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
    def check_due_date(self):
        days_remaining = (self.due_date - datetime.utcnow()).days
        if days_remaining <= 2:  # Notify if the due date is 2 days or less
            message = f'Task "{self.task_name}" is due in {days_remaining} days.'
            self.create_notification(self.group.id, message)

    def create_notification(self, group_id, message):
        # Send notifications to all group members
        group = Group.query.get(group_id)
        for user in group.members:
            notification = Notification(user_id=user.id, message=message)
            db.session.add(notification)
        db.session.commit()
