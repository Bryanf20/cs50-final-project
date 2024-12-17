from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models here
from .user import User
from .group import Group, GroupMember
from .meeting import Meeting
from .resource import Resource
from .chat import GroupChatMessage

