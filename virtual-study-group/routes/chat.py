from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models.chat import ChatGroup, Thread, Message
from models.group import Group

# Define the blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

# Route to display a group chat and threads
@chat_bp.route('/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_chat(group_id):
    group = Group.query.get_or_404(group_id)
    threads = Thread.query.filter_by(group_id=group.id).all()  # Fetch all threads for the group

    if request.method == 'POST':
        content = request.form.get('message')
        thread_id = request.form.get('thread_id')  # Get thread ID for message
        if content and thread_id:
            new_message = Message(
                user_id=current_user.id,
                thread_id=thread_id,
                group_id=group.id,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Message sent!", "success")
        else:
            flash("Message cannot be empty or invalid thread!", "danger")
        return redirect(url_for('chat.group_chat', group_id=group_id))

    return render_template('chat/chat.html', group=group, threads=threads)
    # return render_template('chat/chat.html', group=group)

# Route to create a new thread
@chat_bp.route('/<int:group_id>/thread', methods=['GET', 'POST'])
@login_required
def create_thread(group_id):
    group = Group.query.get_or_404(group_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if title and description:
            new_thread = Thread(
                title=title,
                description=description,
                group_id=group.id
            )
            db.session.add(new_thread)
            db.session.commit()
            flash("New thread created!", "success")
            return redirect(url_for('chat.group_chat', group_id=group.id))
        else:
            flash("Title and description are required.", "danger")

    return render_template('chat/create_thread.html', group=group)

# Thread Detail route
@chat_bp.route('/threads/<int:thread_id>', methods=['GET', 'POST'])
@login_required
def thread_detail(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    messages = Message.query.filter_by(thread_id=thread.id).all()

    if request.method == 'POST':
        content = request.form.get('message')
        if content:
            new_message = Message(
                user_id=current_user.id,
                thread_id=thread.id,
                content=content
            )
            db.session.add(new_message)
            db.session.commit()
            flash("Message sent!", "success")
        else:
            flash("Message cannot be empty!", "danger")
        return redirect(url_for('chat.thread_detail', thread_id=thread.id))

    return render_template('chat/thread_detail.html', thread=thread, messages=messages)
 
