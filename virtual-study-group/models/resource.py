from . import db
# from flask_login import current_user

class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(300), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship('User', back_populates='resources')
    group = db.relationship('Group', back_populates='resources')

    def __repr__(self):
        return f'<Resource {self.title} for Group {self.group_id}>'
