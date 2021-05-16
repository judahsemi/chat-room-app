import datetime

import wtforms
from wtforms import validators
from flask_wtf import FlaskForm

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
        validators=[validators.DataRequired()])
    email = wtforms.StringField(
        "Email",
        validators=[validators.DataRequired()])
    password = wtforms.PasswordField(
        "Password",
        validators=[validators.DataRequired()])

    display = ["name", "def_username", "email", "password"]

    def save(self, commit=True, **kwargs):
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

    display = ["email", "password"]

