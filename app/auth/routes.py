from flask import render_template, redirect, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlsplit

from app import db
from app.auth import bp
from app.auth.forms import LoginForm
from app.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    def get_user(username):
        return db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()

    if current_user.is_authenticated:
        return redirect('main.index')

    login_form = LoginForm()

    if login_form.validate_on_submit():
        user = get_user(login_form.username.data.lower())

        if user is None or not user.check_password(login_form.password.data):
            flash('Invalid username or password')
            return redirect('/')

        login_user(user, remember=login_form.remember_me.data)
        next_page = request.args.get('next')

        if not next_page or urlsplit(next_page).netloc != '':
            next_page = 'main.index'

        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=login_form)


@bp.route('/logout')
def logout():
    if current_user.is_authenticated:
        logout_user()
    return redirect('/')