from flask import Blueprint, jsonify, redirect, url_for
from models import db, Notification
from flask_login import current_user, login_required

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

@notifications_bp.route('/mark_read', methods=['POST'])
@login_required
def mark_notifications_read():
    for notification in current_user.notifications:
        notification.is_read = True
    db.session.commit()
    return jsonify({'status': 'success'})

@notifications_bp.route('/mark-as-read/<int:notification_id>', methods=['GET'])
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    if notification.user_id == current_user.id:
        notification.is_read = True
        db.session.commit()
    return redirect(url_for('group.group_details', group_id=current_user.current_group_id))
