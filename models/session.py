import datetime, random, time

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug, generate_id

import config as cfg
from config import config
from .main import db
from .main import _CRUD, Protected, login_manager



class Session(_CRUD, Protected, db.Model):
    """ """
    __tablename__ = "sessions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.String(16), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), default=None)
    topic = db.Column(db.String(32), nullable=False)
    kind = db.Column(db.String(32), default=cfg.RoomConstant.KIND_OPEN)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    anchor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    rules_id = db.Column(db.Integer, db.ForeignKey("rules.id"), nullable=False)
    participant = db.relationship("ParticipantProfile", backref="session", lazy="dynamic")
    records = db.relationship("Record", backref="session", lazy="dynamic")

    def __init__(self, **kwargs):
        kwargs["number"] = generate_id(time.time(), 16, keylen=4)
        while self.query.filter_by(number=kwargs["number"]).first():
            kwargs["number"] = generate_id(time.time(), 16, keylen=4)

        super(Session, self).__init__(**kwargs)

    @classmethod
    def find(cls, number, secret):
        obj = cls.query.filter((cls.number==number) & (cls.secret==secret)).first()
        return obj

    def __repr__(self):
        return "<Session: %s>" % (self.number)


class Rule(_CRUD, db.Model):
    """ """
    __tablename__ = "rules"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    max_user = db.Column(db.Integer, default=2)
    allow_download = db.Column(db.Boolean, default=True)

    # Relationships
    session = db.relationship("Session", backref="rules", lazy=True, uselist=False)

    def __repr__(self):
        return "<Rule: %s>" % (self.session.number)


class Record(_CRUD, db.Model):
    """ """
    __tablename__ = "records"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    participant_id = db.Column(db.Integer, db.ForeignKey("participant_profiles.id"),
        nullable=True)

    def clean_json(self):
        return {"info": self.info, "category": self.category, "logged_at": self.logged_at,
            "room_number": self.room.number}

    def __repr__(self):
        return "<Record: %s %s>" % (self.session.number, self.category)


class ParticipantProfile(_CRUD, db.Model):
    """ """
    __tablename__ = "participant_profiles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    allow_username_edit = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id"), nullable=False)
    records = db.relationship("Record", backref="participant", lazy="dynamic")

    def __repr__(self):
        return "<Participant Profile: %s %s>" % (self.session.number, self.user.email)

