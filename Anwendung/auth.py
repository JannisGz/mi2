from flask import Blueprint, Flask, redirect, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User
from .extensions import db
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)


@auth.route("/", methods=["GET"])
def login():
    return render_template('login.html', title="Login")


@auth.route("/", methods=["POST"])
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')
    remember = True

    user = User.query.filter_by(username=username).first()

    # Überprüfe Zugangsdaten
    if not user or not check_password_hash(user.password, password):

        # Bei ungültigen Zugangsdaten auf Login-Seite zurück mit Fehlermeldung
        flash('Ungültige Zugangsdaten.', 'error')
        return redirect(url_for('auth.login'))

    # Bei gültigen Zugangsdaten auf die Home-Seite weiterleiten
    login_user(user, remember=remember)
    return redirect(url_for('main.patients'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login', titel="Login"))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    username = request.form.get('username')
    name = request.form.get('username')
    password = request.form.get('password')

    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, username=username,password=generate_password_hash(password, method='sha256'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))
