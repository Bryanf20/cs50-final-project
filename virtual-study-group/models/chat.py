from datetime import datetime
from . import db

class GroupChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('group_chat_messages', lazy=True))
    group = db.relationship('Group', backref=db.backref('chat_messages', lazy=True))

    def __repr__(self):
        return f'<GroupChatMessage {self.id} - {self.content[:30]}...>'
