from . import db

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    members = db.relationship('GroupMember', backref='group', lazy='dynamic')
    
    resources = db.relationship('Resource', back_populates='group', cascade='all, delete-orphan')
    # messages = db.relationship('Message', backref='group', lazy='dynamic')
    # threads = db.relationship('Thread', backref='group', lazy='dynamic') 

    def __repr__(self):
        return f'<Group {self.name}>'
    

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'<GroupMember user_id={self.user_id} group_id={self.group_id}>'
    
    
class GroupInvite(db.Model):
    __tablename__ = 'group_invites'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)  # Group FK
    email = db.Column(db.String(120), nullable=False)  # Email of the invitee
    invite_code = db.Column(db.String(36), unique=True, nullable=False)  # UUID for the invite
    invited_at = db.Column(db.DateTime, server_default=db.func.now())
    accepted = db.Column(db.Boolean, default=False)


# class Meeting(db.Model):
#     __tablename__ = 'meetings'
#     id = db.Column(db.Integer, primary_key=True)
#     group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)  # Group FK
#     title = db.Column(db.String(200), nullable=False)  # Meeting title
#     date_time = db.Column(db.DateTime, nullable=False)  # Date and time of the meeting
#     link = db.Column(db.String(300), nullable=True)  # Meeting link (e.g., Zoom/Google Meet)
#     created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # User FK
#     created_at = db.Column(db.DateTime, server_default=db.func.now())
