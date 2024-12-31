from datetime import datetime
from . import db

class Notification(db.Model):
    # __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_real_time_sent = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

    user = db.relationship('User', backref='notifications')

    def __repr__(self):
        return f'<Notification {self.message}>'
