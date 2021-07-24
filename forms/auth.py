import datetime

import wtforms
from wtforms import validators, ValidationError
from flask_wtf import FlaskForm
from flask_login import login_required, login_user, logout_user

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log

# from utils.helper import generate_slug



class RegisterForm(FlaskForm):
    name = wtforms.StringField(
        "Name",
        validators=[validators.DataRequired()])
    def_username = wtforms.StringField(
        "Default Username",
        validators=[validators.DataRequired(), validators.Length(min=4, max=25)])
    email = wtforms.StringField(
        "Email",
        validators=[validators.DataRequired()])
    password = wtforms.PasswordField(
        "Password",
        validators=[validators.DataRequired()])

    display = ["name", "def_username", "email", "password"]

    def validate_def_username(self, def_username):
        user = User.query.filter_by(def_username=def_username.data).first()
        if user:
            raise ValidationError("This username has already been taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("Account with this email already exists.")

    def save(self, commit=True, **kwargs):
        """ Create a new user """
        user = User(
            name=self.name.data,
            def_username=self.def_username.data,
            email=self.email.data,
            password=self.password.data,
            **kwargs).add(commit=commit)
        return user


class LoginForm(FlaskForm):
    email = wtforms.StringField(
        "Email",
        validators=[validators.DataRequired()])
    password = wtforms.PasswordField(
        "Password",
        validators=[validators.DataRequired()])

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError("")

    def validate_password(self, password):
        user = User.authenticate(User.email == self.email.data, password=password.data)
        if not user:
            raise ValidationError("Email or password is incorrect.")

    display = ["email", "password"]

    def save(self, user, remember):
        """ Login a user """
        login_user(user, remember=remember)
        return user

