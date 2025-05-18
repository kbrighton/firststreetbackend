from typing import Optional, Union
from flask import render_template, redirect, flash, request, Response
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlsplit

from app.extensions import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login() -> Union[str, Response]:
    """
    Handle user login.

    This route handles both displaying the login form (GET) and
    processing form submissions to authenticate users (POST).

    Returns:
        On GET: Rendered HTML template with the login form.
        On POST: Redirect to the home page after successful login,
                or rendered form with error messages if authentication fails.
    """
    def get_user(username: str) -> Optional[User]:
        return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    if current_user.is_authenticated:
        return redirect('/')

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = get_user(login_form.username.data.lower())

        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect('/')

        login_user(user, remember=login_form.remember_me.data)

        return redirect('/')

    return render_template('auth/login.html', title='Sign In', form=login_form)


@bp.route('/logout')
def logout() -> Response:
    """
    Handle user logout.

    This route logs out the current user and redirects to the home page.

    Returns:
        Redirect to the home page.
    """
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')
