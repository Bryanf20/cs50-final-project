from flask import request, redirect, url_for, flash, Blueprint, render_template
from flask_login import login_required, current_user
from app import db, socketio
from models import Group, GroupChatMessage
from flask_socketio import emit
from datetime import datetime


chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Route for Posting a Message via HTTP
@chat_bp.route('/<int:group_id>/post_message', methods=['POST'])
@login_required
def post_message_http(group_id):
    group = Group.query.get_or_404(group_id)
    content = request.form.get('content')
    
    if not content:
        flash("Message content is required", "warning")
        return redirect(url_for('groups.group_details', group_id=group.id))
    
    # Check if the user is a member
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups.view_groups'))
    
    # Create a new chat message
    message = GroupChatMessage(content=content, user_id=current_user.id, group_id=group_id)
    
    # Add the message to the database
    db.session.add(message)
    db.session.commit()
    
    # Emit message to all connected clients (Used ChatGPT)
    socketio.emit('new_message', {
        'user': current_user.username, 
        'content': content,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }, namespace='/chat')
    flash("Message posted successfully", "success")
    return redirect(url_for('chat.view_chat', group_id=group_id))


# WebSocket Event for Posting a Message (Used ChatGPT)
@socketio.on('post_message', namespace='/chat')
def post_message_socketio(data):
    try:
        group_id = data.get('group_id')
        content = data.get('content')
        group = Group.query.get_or_404(group_id)
        
        if not content:
            return
        
        # Check if the user is a member
        if not current_user.is_member_of(group):
            flash('You are not a member of this group.', 'danger')
            return redirect(url_for('groups.view_groups'))

        # Process the message as usual
        group = Group.query.get_or_404(group_id)
        message = GroupChatMessage(content=content, user_id=current_user.id, group_id=group.id)
        db.session.add(message)
        db.session.commit()
        
        # Emit to others
        socketio.emit('new_message', {
            'user': current_user.username, 
            'content': content,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }, namespace='/chat')
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('typing', namespace='/chat')
def typing(data):
    emit('typing', {'user': data['user']}, broadcast=True, include_self=False)

@socketio.on('stop_typing', namespace='/chat')
def stop_typing():
    emit('stop_typing', broadcast=True, include_self=False)


# Route for Viewing Messages
@chat_bp.route('/<int:group_id>/view_chat')
@login_required
def view_chat(group_id):
    group = Group.query.get_or_404(group_id)

    # Check if the user is a member
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups.view_groups'))
    
    # Fetch all messages in the group, sorted by timestamp
    messages = GroupChatMessage.query.filter_by(group_id=group_id).order_by(GroupChatMessage.timestamp).all()
    
    return render_template('chat/view_chat.html', group=group, messages=messages)
