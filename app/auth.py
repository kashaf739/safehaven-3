# app/auth.py

from flask import Blueprint, redirect, url_for, render_template
from flask_login import login_user, login_required, logout_user, current_user
from app.models import User
from app.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    print("login function")
    if current_user.is_authenticated:
        print("login auth sucess")
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    print("login instanse created")
    if form.validate_on_submit():
        print("validation sucess")
        user = User.query.filter_by(email=form.email.data).first()
        print("user", user)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            print("user trying to login")
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            print("login sucess")
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your email or password.', 'danger')
            print("login faild")
        
    print("bring template")
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))
