import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug, assert_access

import config as cfg
from config import config
from .main import db
from .main import _CRUD, Protected, login_manager



class Settings(_CRUD, db.Model):
    """ """
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    max_user = db.Column(db.Integer, default=2)
    allow_download = db.Column(db.Boolean, default=True)

    # Relationships
    room = db.relationship("Room", backref="settings", lazy=True, uselist=False)

    def __repr__(self):
        return "<Settings: %s>" % (self.room.number)


class Log(_CRUD, db.Model):
    """ """
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(32), nullable=True)
    logged_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    def clean_json(self):
        return {"info": self.info, "category": self.category, "username": self.username,
        "logged_at": self.logged_at, "room_number": self.room.number}

    def __repr__(self):
        return "<Log: %s %s>" % (self.room.number, self.category)

