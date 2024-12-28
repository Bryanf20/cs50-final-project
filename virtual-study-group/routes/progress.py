from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from models.task_progress import TaskProgress
from models.group import Group

progress_bp = Blueprint('progress', __name__, url_prefix='/progress')

# Route to view tasks for a group
@progress_bp.route('/<int:group_id>', methods=['GET'])
@login_required
def view_progress(group_id):
    group = Group.query.get_or_404(group_id)
    # tasks = TaskProgress.query.filter_by(group_id=group.id).all()
    query = TaskProgress.query.filter_by(group_id=group_id)

    # Search by task name
    search_query = request.args.get('search')
    if search_query:
        query = query.filter(TaskProgress.task_name.ilike(f'%{search_query}%'))

    # Filter by status
    status_filter = request.args.get('status')
    if status_filter:
        query = query.filter_by(status=status_filter)

    # Filter by assigned user
    assigned_to_filter = request.args.get('assigned_to')
    if assigned_to_filter:
        query = query.filter_by(assigned_to=assigned_to_filter)

    tasks = query.order_by(TaskProgress.due_date.asc()).all()

    # Calculate progress
    completed_tasks = query.filter_by(status='Completed').count()
    total_tasks = query.count()
    progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

    return render_template('progress/view_progress.html', group=group, tasks=tasks, progress=progress_percentage)

# Route to add a new task
@progress_bp.route('/<int:group_id>/add', methods=['POST'])
@login_required
def add_task(group_id):
    group = Group.query.get_or_404(group_id)
    task_name = request.form.get('task_name')
    # due_date = request.form.get('due_date')
    due_date_str = request.form.get('due_date')  # Input from the form (e.g., '2024-12-04')
    assigned_to = request.form.get('assigned_to')

    # Convert the string to a datetime object
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('task.add_task'))  # Handle invalid date format
    else:
        due_date = None

    if not task_name:
        flash('Task name is required.', 'danger')
        return redirect(url_for('progress.view_progress', group_id=group.id))

    # Add new task
    task = TaskProgress(
        group_id=group.id,
        task_name=task_name,
        due_date=due_date,
        assigned_to=assigned_to
    )
    db.session.add(task)
    db.session.commit()

    # Check for notifications (e.g., task close to deadline)
    task.check_due_date()
    flash('Task added successfully.', 'success')
    return redirect(url_for('progress.view_progress', group_id=group.id))

# Route to update a task's status
@progress_bp.route('/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_status(task_id):
    task = TaskProgress.query.get_or_404(task_id)
    new_status = request.form.get('status')

    if new_status not in ['Pending', 'Completed']:
        flash('Invalid status value.', 'danger')
        return redirect(url_for('progress.view_progress', group_id=task.group_id))

    task.status = new_status
    db.session.commit()

    # Notify group members about status change
    task.create_notification(task.group_id, f'Task "{task.task_name}" status updated to {task.status}.')
    flash('Task status updated.', 'success')
    return redirect(url_for('progress.view_progress', group_id=task.group_id))

# Route to edit/update a task
@progress_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = TaskProgress.query.get_or_404(task_id)
    group = Group.query.get_or_404(task.group_id)

    # Ensure the current user belongs to the group managing the task
    if not current_user.is_member_of(group):
        flash("You do not have permission to edit this task.", "danger")
        return redirect(url_for('groups.group_details', group_id=task.group_id))

    if request.method == 'POST':
        task_name = request.form.get('task_name')
        due_date = request.form.get('due_date')
        status = request.form.get('status')

        if not task_name or not due_date or not status:
            flash("All fields are required.", "warning")
            return redirect(request.url)

        try:
            task.task_name = task_name
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
            task.status = status

            db.session.commit()
            flash("Task updated successfully!", "success")
            return redirect(url_for('groups.group_details', group_id=task.group_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the task.", "danger")
            print(str(e))  # Debugging
            return redirect(request.url)

    return render_template('progress/edit_task.html', task=task)

# Route to delete a task
@progress_bp.route('/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = TaskProgress.query.get_or_404(task_id)
    group = Group.query.get_or_404(task.group_id)

    # Ensure the current user has permission
    if not current_user.is_member_of(group):
        flash("You do not have permission to delete this task.", "danger")
        return redirect(url_for('groups.group_details', group_id=task.group_id))

    try:
        db.session.delete(task)
        db.session.commit()
        flash("Task deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("An error occurred while deleting the task.", "danger")
        print(str(e))

    return redirect(url_for('groups.group_details', group_id=task.group_id))
