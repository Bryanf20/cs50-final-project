# from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_from_directory
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from app import db, mail, files, app
from models.user import User
from models.group import Group, GroupMember, GroupInvite
from models.meeting import Meeting
from models.resource import Resource
from models.task_progress import TaskProgress
# from models.notification import Notification
from forms.group_form import GroupForm
from forms.accept_invite_form import AcceptInviteForm
from forms.edit_group_form import EditGroupForm
from forms.schedule_meeting_form import ScheduleMeetingForm
from forms.resource_form import ResourceUploadForm
import uuid
from flask_mail import Message


groups_bp = Blueprint('groups', __name__, url_prefix='/groups')

# Route to create a group
@groups_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_group():
    form = GroupForm()
    if form.validate_on_submit():
        # Create the group
        group = Group(
            name=form.name.data,
            description=form.description.data,
            created_by=current_user.id
        )
        db.session.add(group)
        db.session.commit()

        # Automatically add the creator as a member
        member = GroupMember(user_id=current_user.id, group_id=group.id)
        db.session.add(member)
        db.session.commit()

        flash('Study group created and you have been added as a member!', 'success')
        return redirect(url_for('home.home'))
    return render_template('groups/create.html', form=form)



# Route to list groups
@groups_bp.route('/', methods=['GET'])
@login_required
def view_groups():
    # user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user.id).all()
    groups = Group.query.all()
    # return render_template('groups/view.html', groups=user_groups)
    return render_template('groups/view.html', groups=groups)


# Group details
@groups_bp.route('/<int:group_id>')
@login_required
def group_details(group_id):
    group = Group.query.get_or_404(group_id)

    # Check if the user is a member
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('groups.view_groups'))
    
    group_members = GroupMember.query.filter_by(group_id=group_id).all()
    members = []
    for group_mem in group_members:
        members.append(User.query.filter_by(id=group_mem.user_id).first())
    resources = Resource.query.filter_by(group_id=group.id).all()
    meetings = Meeting.query.filter_by(group_id=group.id).order_by(Meeting.date_time).all()
    tasks = TaskProgress.query.filter_by(group_id= group_id).all()

    # Calculate task progress
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == 'Completed')
    progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # # Check for tasks due within 24 hours
    # now = datetime.utcnow()
    # for task in tasks:
    #     if task.status == 'Pending' and task.due_date - now <= timedelta(hours=24):
    #         # Create a notification for the user
    #         notification = Notification(
    #             user_id=current_user.id,
    #             message=f"Task '{task.task_name}' is due soon!",
    #         )
    #         db.session.add(notification)
    # db.session.commit()
    
    return render_template('groups/group_details.html',
                           group=group,
                           resources=resources,
                           members=members,
                           meetings=meetings,
                           tasks=tasks,
                           progress=progress_percentage,
                           current_user=current_user)


# Route to join a group
@groups_bp.route('/join/<int:group_id>', methods=['GET', 'POST'])
@login_required
def join_group(group_id):
    group = Group.query.get_or_404(group_id)
    if not GroupMember.query.filter_by(user_id=current_user.id, group_id=group.id).first():
        member = GroupMember(user_id=current_user.id, group_id=group.id)
        db.session.add(member)
        db.session.commit()
        flash('You joined the group!', 'success')
    else:
        flash('You are already a member of this group.', 'warning')
    return redirect(url_for('groups.group_details', group_id=group_id))


# Route for Sending Invites
@groups_bp.route('/invite_member/<int:group_id>', methods=['GET'])
@login_required
def invite_member(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template('groups/invite.html', group=group)

@groups_bp.route('/<int:group_id>/invite', methods=['POST'])
@login_required
def send_invite(group_id):
    group = Group.query.get_or_404(group_id)
    if group.created_by != current_user.id:
        flash('Only the group admin can send invites.', 'danger')
        return redirect(url_for('groups.view_groups'))

    email = request.form.get('email')
    if not email:
        flash('Please provide an email address.', 'warning')
        return redirect(url_for('groups.invite_member', group_id=group_id))
    
    invite_code = str(uuid.uuid4())
    invite = GroupInvite(group_id=group.id, email=email, invite_code=invite_code)
    db.session.add(invite)
    db.session.commit()

    # Send email with the invite link (Was assisted by ChatGPT)
    invite_link = url_for('groups.accept_invite', invite_code=invite_code, _external=True)
    msg = Message('You are invited to join a study group', recipients=[email])
    msg.body = f"You've been invited to join the group '{group.name}'. Click the link to join: {invite_link}"
    
    try:
        mail.send(msg)
        flash('Invite sent successfully!', 'success')
    except Exception as e:  # Catch potential internet connection issues  # noqa: F841
        db.session.rollback()  # Rollback the DB transaction if needed
        flash('Failed to send the invite. Please check your internet connection.', 'danger')
        return redirect(url_for('groups.group_details', group_id=group_id))

    return redirect(url_for('groups.group_details', group_id=group_id))



# Route for Accepting Invites
@groups_bp.route('/invite/<invite_code>', methods=['GET', 'POST'])
@login_required
def accept_invite(invite_code):
    invite = GroupInvite.query.filter_by(invite_code=invite_code, accepted=False).first_or_404()
    group = Group.query.get(invite.group_id)

    form = AcceptInviteForm()

    if request.method == 'POST':
        # Add user to group
        member = GroupMember(user_id=current_user.id, group_id=group.id)
        db.session.add(member)
        invite.accepted = True
        db.session.commit()

        flash(f'You have joined the group {group.name}!', 'success')
        return redirect(url_for('groups.group_details', group_id=group.id))

    return render_template('groups/accept_invite.html', group=group, form=form)


# Route for Editing Groups
@groups_bp.route('/<int:group_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_group(group_id):
    group = Group.query.get_or_404(group_id)
    if group.created_by != current_user.id:
        flash('Only the group admin can edit group details.', 'danger')
        return redirect(url_for('groups.group_details', group_id=group.id))
    
    form = EditGroupForm(obj=group)
    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        db.session.commit()
        flash('Group details updated successfully!', 'success')
        return redirect(url_for('groups.group_details', group_id=group.id))
    
    return render_template('groups/edit.html', form=form, group=group)

# Route to Schedule a Meeting
@groups_bp.route('/<int:group_id>/schedule', methods=['GET', 'POST'])
@login_required
def schedule_meeting(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure only group members can schedule meetings
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'warning')
        return redirect(url_for('home.home'))

    form = ScheduleMeetingForm()

    if form.validate_on_submit():
        print("Form data:", request.form)  # Debug raw form data
        print("Parsed date_time:", form.date_time.data)  # Debug parsed data

        meeting = Meeting(
            title=form.title.data,
            date_time=form.date_time.data,
            link=form.link.data,
            group_id=group.id,
            created_by=current_user.id
        )
        db.session.add(meeting)
        db.session.commit()

        flash('Meeting scheduled successfully!', 'success')
        return redirect(url_for('groups.group_details', group_id=group.id))
    else:
        print("Form errors:", form.errors)  # Debug form validation errors

    # return render_template('schedule_meeting.html', form=form, group=group)
    return render_template('groups/schedule_meeting.html', form=form, group=group)

# Route to List Meetings
@groups_bp.route('/<int:group_id>/meetings', methods=['GET'])
@login_required
def list_meetings(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure only group members can view meetings
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'warning')
        return redirect(url_for('home.home'))

    meetings = Meeting.query.filter_by(group_id=group.id).order_by(Meeting.date_time).all()
    return render_template('groups/meetings.html', group=group, meetings=meetings)

# Route to Delete a Meeting
@groups_bp.route('/<int:group_id>/delete_meeting/<int:meeting_id>', methods=['POST'])
@login_required
def delete_meeting(group_id, meeting_id):
    group = Group.query.get_or_404(group_id)
    meeting = Meeting.query.get_or_404(meeting_id)

    # Ensure only group members can delete meetings
    if not current_user.is_member_of(group):
        flash('You are not authorized to delete this meeting.', 'warning')
        return redirect(url_for('home.home'))

    # Delete the meeting
    db.session.delete(meeting)
    db.session.commit()

    flash('Meeting deleted successfully.', 'success')
    return redirect(url_for('groups.group_details', group_id=group_id))


# Route for uploads
@groups_bp.route('/<int:group_id>/upload', methods=['GET', 'POST'])
@login_required
def upload_resource(group_id):
    group = Group.query.get_or_404(group_id)
    if not current_user.is_member_of(group):
        flash('You must be a member of the group to upload resources.')
        return redirect(url_for('home.home'))

    form = ResourceUploadForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = files.save(file, name=filename)  # Save the file
        resource = Resource(
            title=form.title.data,
            file_path=file_path,
            uploaded_by=current_user.id,
            group_id=group.id
        )
        db.session.add(resource)
        db.session.commit()
        flash('Resource uploaded successfully!', 'success')
        return redirect(url_for('groups.group_details', group_id=group.id))

    return render_template('groups/upload_resource.html', form=form, group=group)


# Downloads
@groups_bp.route('/uploads/<filename>')
@login_required
def download_file(filename):
    return send_from_directory(app.config['UPLOADED_FILES_DEST'], filename, as_attachment=True)


# Leave Group
@groups_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave_group(group_id):
    group = Group.query.get_or_404(group_id)
    # Check if the user is the group creator
    if group.created_by == current_user.id:
        flash('Group creators cannot leave the group. Please delete or transfer ownership first.', 'warning')
        return redirect(url_for('groups.group_details', group_id=group_id))
    
    # Check if the user is a member
    if not current_user.is_member_of(group):
        flash('You are not a member of this group.', 'danger')
        return redirect(url_for('home.home'))
    
    # Remove the user from the group
    membership = GroupMember.query.filter_by(user_id=current_user.id, group_id=group_id).first()
    db.session.delete(membership)
    db.session.commit()

    flash("You have successfully left the group.", "success")
    return redirect(url_for('home.home'))


# Route for Removing a Member
@groups_bp.route('/<int:group_id>/remove_member', methods=['POST'])
@login_required
def remove_member(group_id):
    # Parse data from form submission (or query parameters)
    user_id = request.form.get('user_id') or request.args.get('user_id')

    # Validate user_id in request
    if not user_id:
        flash("User ID is required", "warning")
        return redirect(url_for('groups.group_details', group_id=group_id))

    try:
        user_id = int(user_id)
    except ValueError:
        flash("Invalid User ID", "danger")
        return redirect(url_for('groups.group_details', group_id=group_id))

    # Fetch the group
    group = Group.query.get_or_404(group_id)

    if user_id == group.created_by:
        flash("Group creator cannot be removed from the group", "danger")
        return redirect(url_for('groups.group_details', group_id=group_id))

    # Check if the current user has permission to remove members
    if current_user.id != group.created_by and current_user.role != 'admin':
        flash("Permission denied", "danger")
        return redirect(url_for('groups.group_details', group_id=group_id))

    # Check if the user to be removed is a member of the group
    member = GroupMember.query.filter_by(group_id=group_id, user_id=user_id).first()
    if not member:
        flash("User is not a member of the group", "warning")
        return redirect(url_for('groups.group_details', group_id=group_id))

    # Remove the user from the group
    try:
        db.session.delete(member)
        db.session.commit()
        flash("User removed from the group successfully", "success")
    except Exception as e:  # noqa: F841
        db.session.rollback()
        flash("An error occurred while removing the member", "danger")

    return redirect(url_for('groups.group_details', group_id=group_id))

# Route for Deleting a Group
@groups_bp.route('/<int:group_id>/delete', methods=['POST'])
@login_required
def delete_group(group_id):
    group = Group.query.get_or_404(group_id)

    # Ensure only the group creator or an admin can delete the group
    if current_user.id != group.created_by and current_user.role != 'admin':
        flash("You do not have permission to delete this group.", "danger")
        return redirect(url_for('groups.group_details', group_id=group_id))

    try:
        # Delete the group and associated data
        db.session.delete(group)
        db.session.commit()
        flash("Group deleted successfully.", "success")
        return redirect(url_for('home.home'))
    except Exception:
        db.session.rollback()
        flash("An error occurred while deleting the group.", "danger")
        return redirect(url_for('groups.group_details', group_id=group_id))

