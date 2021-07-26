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
    """
    name: The real and full-name of the user.
    def_username: A username that only the user can have in any room or session.
    email: User email, used for logging in.
    password_hash: Hash of account password.
    """
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
    memb_profiles = db.relationship("MemberProfile", backref="user", lazy="dynamic")
    notifications = db.relationship("Notification", backref="receiver", lazy="dynamic")

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def unread_notes(self):
        return self.notifications.filter_by(is_read=False).all()

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


class Notification(_CRUD, db.Model):
    """
    info: The text-message of the notification.
    action_name: A verb that describes what the user should do with the info.
    action_link: A link that takes the user to where they should go.
    is_read: Indicates if the notification has been seen by the user.
    """
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info = db.Column(db.Text, nullable=False)
    action_name = db.Column(db.String(32), nullable=True)
    action_link = db.Column(db.Text, nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    received_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    def __repr__(self):
        return "<Notification: %s %s>" % (self.receiver.name, self.is_read)

