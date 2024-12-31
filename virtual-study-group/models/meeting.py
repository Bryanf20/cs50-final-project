from . import db
from models.notification import Notification
from models.group import Group
from datetime import datetime, timedelta

class Meeting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    link = db.Column(db.String(300), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<Meeting {self.id} for Group {self.group_id}>'

    # Reminder
    def create_notification(self, group_id, message):
        # Send notifications to all group members
        group = Group.query.get(group_id)
        for user in group.members:
            existing_notification = Notification.query.filter_by(
                user_id=user.id,
                message=message,
                is_read=False
            ).first()

            # Avoid duplicate notifications
            if not existing_notification:
                notification = Notification(user_id=user.id, message=message, due_date=self.date_time)
                db.session.add(notification)
        db.session.commit()

    from datetime import datetime, timedelta

    def check_reminders(self):
        now = datetime.utcnow()

        # Calculate reminder thresholds
        one_day_before = self.date_time - timedelta(days=1)
        two_hours_before = self.date_time - timedelta(hours=2)

        # Check if it's time to send a "less than a day" reminder
        if one_day_before <= now < two_hours_before:
            message = f'Reminder: The meeting "{self.title}" is in less than a day. Join using the link: {self.link}'
            self.create_notification(self.group_id, message)

        # Check if it's time to send a "less than 2 hours" reminder
        elif two_hours_before <= now < self.date_time:
            message = f'Reminder: The meeting "{self.title}" is in less than 2 hours. Join using the link: {self.link}'
            self.create_notification(self.group_id, message)
