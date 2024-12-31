from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default='member')  # 'admin' or 'member'
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Define relationships
    memberships = db.relationship('GroupMember', backref='user', lazy=True)
    resources = db.relationship('Resource', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', cascade='all, delete-orphan', passive_deletes=True)
    # group_chat_messages = db.relationship('GroupChatMessage', backref='user', cascade='all, delete-orphan', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Required by Flask-Login
    def get_id(self):
        return str(self.id)

    # Optional, but may be helpful
    @property
    def is_active(self):
        return True  # Or add custom logic if you support user activation/deactivation

    @property
    def is_authenticated(self):
        return True  # Flask-Login manages this for you in most cases

    @property
    def is_anonymous(self):
        return False  # User models are never anonymous

    def __repr__(self):
        return f'<User {self.username}>'

    def is_member_of(self, group):
        # Use the `memberships` relationship to check membership
        return any(membership.group_id == group.id for membership in self.memberships)
