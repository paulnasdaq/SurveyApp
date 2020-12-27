from flask import Blueprint, flash, redirect, url_for, request, render_template
from flask_login import current_user, login_user, logout_user, login_required

from app import login_manager, db
from .forms import LoginForm, SignupForm
from .models import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@login_manager.unauthorized_handler
def unauthorized_login():
    flash("You must be logged in to access this page")
    return redirect(url_for('auth.login'))


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None







@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            flash(f'Welcome to SurveyApp, {current_user.first_name} {current_user.last_name}')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please Check your email and password. Sign up if you do not have an account')
    return render_template('auth/login.html', title='Login', form=form)










@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))







@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = SignupForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        
        if existing_user is None:
            user = User(email=form.email.data, first_name=form.first_name.data, last_name=form.last_name.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created successfully')
            return redirect(url_for('auth.login'))
        flash('A user already exists with that email address, please use another one.')
    return render_template('auth/register.html', title='Sign Up', form=form)
