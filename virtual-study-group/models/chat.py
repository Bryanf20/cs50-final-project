# from datetime import datetime, timezone
from . import db

class ChatGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    # messages = db.relationship('Message', back_populates='group', lazy=True)

class Thread(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    # created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    # messages = db.relationship('Message', back_populates='thread', lazy=True)

    group = db.relationship('Group', backref='thread', lazy=True)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    # timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    timestamp = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', backref='messages', lazy=True)
    thread = db.relationship('Thread', backref='messages', lazy=True)
    group = db.relationship('Group', backref='messages', lazy=True)
