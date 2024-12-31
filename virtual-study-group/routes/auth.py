from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from models.user import User
from models.task_progress import TaskProgress
from models import db
from sqlalchemy import and_, or_
from forms.login_form import LoginForm
from forms.register_form import RegistrationForm
from app import generate_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created. You can now log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            tasks = TaskProgress.query.filter(
                and_(TaskProgress.status == "Pending",
                     or_(TaskProgress.assigned_to == user.id,
                         TaskProgress.assigned_to == None  # noqa: E711
                    )
                )
            ).all()
            for task in tasks:
                task.check_due_date(task.assigned_to)
            flash('Login Successful.', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home.home'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    elif request.method == 'POST':
        flash('Invalid input. Please check the entered email and password.', 'warning')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_new_password = request.form.get('confirm_new_password')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('auth.change_password'))

        if new_password != confirm_new_password:
            flash('New passwords do not match.', 'warning')
            return redirect(url_for('auth.change_password'))

        # Update the user's password
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash('Your password has been updated.', 'success')
        return redirect(url_for('home.home'))

    return render_template('change_password.html')


@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = current_user.id
    logout_user()
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        flash('Your account has been deleted.', 'info')
    return redirect(url_for('auth.register'))
