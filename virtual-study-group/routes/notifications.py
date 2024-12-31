from flask import Blueprint, jsonify
from models import db
from flask_login import current_user, login_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})

