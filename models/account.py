import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug, assert_access

import config as cfg
from config import config
from .main import db
from .main import _CRUD, Protected, login_manager



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(_CRUD, Protected, db.Model):
    """ """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    def_username = db.Column(db.String(32), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    owned_rooms = db.relationship("Room", backref="admin", lazy="dynamic")
    logs = db.relationship("Log", backref="user", lazy="dynamic")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    # Flask-Login Requirement
    def get_id(self):
        return str(self.id)

    # Flask-Login Requirement
    def is_authenticated(self):
        return True

    # Flask-Login Requirement
    def is_active(self):
        return True

    # Flask-Login Requirement
    def is_anonymous(self):
        return False

    def __repr__(self):
        return "<User: %s %s>" % (self.name, self.email)

