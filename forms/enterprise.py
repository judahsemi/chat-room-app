import datetime, shutil, time

import wtforms
from wtforms import validators
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, send, emit

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log, Enterprise, EmployeeProfile

from utils.helper import generate_slug, generate_id



class CreateEnterpriseForm(FlaskForm):
    name = wtforms.StringField(
        "Name",
        validators=[validators.DataRequired()])
    about = wtforms.StringField(
        "About",
        validators=[validators.DataRequired()])

    display = ["name", "about"]

    def save(self, user, commit=True, **kwargs):
        enterprise = Enterprise(
            name=self.name.data,
            about=self.about.data,
            admin=user,
            **kwargs).add(commit=commit)

        admin_profile = EmployeeProfile(
            username=user.def_username,
            email=user.email,
            user=user,
            enterprise=enterprise).add(commit=commit)
        return enterprise


class EditEmployeeProfileForm(FlaskForm):
    username = wtforms.StringField(
        "Username",
        validators=[validators.DataRequired()])
    email = wtforms.StringField(
        "Email",
        validators=[validators.DataRequired()])

    display = ["username", "email"]

    def save(self, profile, commit=True, **kwargs):
        profile.update(
            commit=commit,
            username=self.username.data,
            email=self.email.data,
            **kwargs)
        return profile

