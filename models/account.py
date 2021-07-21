import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug

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
    owned_enterprises = db.relationship("Enterprise", backref="admin", lazy="dynamic")
    emp_profiles = db.relationship("EmployeeProfile", backref="user", lazy="dynamic")
    owned_rooms = db.relationship("Room", backref="admin", lazy="dynamic")
    memb_profiles = db.relationship("MemberProfile", backref="user", lazy="dynamic")

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


class Enterprise(_CRUD, db.Model):
    """ """
    __tablename__ = "enterprises"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    about = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    employees = db.relationship("EmployeeProfile", backref="enterprise", lazy="dynamic")
    rooms = db.relationship("Room", backref="enterprise", lazy="dynamic")

    def __repr__(self):
        return "<Enterprise: %s>" % (self.name)


class EmployeeProfile(_CRUD, db.Model):
    """ """
    __tablename__ = "employee_profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    enterprise_id = db.Column(db.Integer, db.ForeignKey("enterprises.id"), nullable=False)

    def __repr__(self):
        return "<Employee Profile: %s %s>" % (self.enterprise.name, self.user.email)

