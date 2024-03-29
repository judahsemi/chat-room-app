import datetime, random, time

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug, generate_id, encode_token, decode_token

import config as cfg
from config import config
from .main import db
from .main import _CRUD, Protected, login_manager



class Room(_CRUD, Protected, db.Model):
    """
    number: Unique string used for identifying a room.
    password_hash: Hash of room password if there is one.
    topic: The room topic.
    kind: Used for determining the scope of the room.
    is_active: Indicates if a room has been fully-created.
    """
    __tablename__ = "rooms"
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
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    settings_id = db.Column(db.Integer, db.ForeignKey("settings.id"), nullable=False)
    members = db.relationship("MemberProfile", backref="room", lazy="dynamic")
    logs = db.relationship("Log", backref="room", lazy="dynamic")

    def __init__(self, **kwargs):
        kwargs["number"] = generate_id(time.time(), 16, keylen=4)
        while self.query.filter_by(number=kwargs["number"]).first():
            kwargs["number"] = generate_id(time.time(), 16, keylen=4)

        super(Room, self).__init__(**kwargs)

    @classmethod
    def recommended(cls, admin_user, rooms=None, topk=10):
        rooms = rooms or cls.query.filter_by(is_active=True, admin=admin_user)
        return cls.newest(rooms=rooms, topk=topk)

    @classmethod
    def newest(cls, rooms=None, topk=10):
        rooms = rooms or cls.query.filter_by(is_active=True)
        return rooms.order_by(cls.created_at.desc()).all()[:topk]

    @classmethod
    def popular(cls, rooms=None, topk=10):
        rooms = rooms or cls.query.filter_by(is_active=True)
        non_admin_rooms = [r for r in rooms.all() if r.admin.def_username != "admin"]
        return sorted(non_admin_rooms, key=lambda x: len(x.members.all()))[::-1][:topk]

    @classmethod
    def most_active(cls, rooms=None, topk=10):
        rooms = rooms or cls.query.filter_by(is_active=True)
        non_admin_rooms = [r for r in rooms.all() if r.admin.def_username != "admin"]
        return sorted(non_admin_rooms, key=lambda x: len(x.logs.all()))[::-1][:topk]

    def generate_join_token(self):
        return str(encode_token({"id": self.id, "number": self.number}))[2:-1]

    @classmethod
    def validate_join_token(cls, token):
        is_valid, data = decode_token(token)
        if is_valid and isinstance(data, dict):
            return cls.query.filter_by(id=data.get("id"), number=data.get("number")).first()
        return is_valid

    def get_user_username(self, user):
        logs = user.logs.filter_by(room=self).all()
        for log in logs:
            if log.username:
                return log.username
        return None

    def get_user_with_username(self, username):
        logs = self.logs.filter_by(username=username).all()
        for log in logs:
            if log.user:
                return log.user
        return None

    @classmethod
    def find(cls, number, secret):
        obj = cls.query.filter((cls.number==number) & (cls.secret==secret)).first()
        return obj

    def __repr__(self):
        return "<Room: %s>" % (self.number)


class Settings(_CRUD, db.Model):
    """
    max_user: Maximum number of active room members at any one time.
    allow_download: Indicates if members (excluding the admin) can download room logs.
    """
    __tablename__ = "settings"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    max_user = db.Column(db.Integer, default=2)
    allow_download = db.Column(db.Boolean, default=True)

    # Relationships
    room = db.relationship("Room", backref="settings", lazy=True, uselist=False)

    def __repr__(self):
        return "<Settings: %s>" % (self.room.number)


class Log(_CRUD, db.Model):
    """
    info: The text-message of the log.
    category: The log type, used for determing where and how the message is displayed.
    """
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    info = db.Column(db.Text, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    logged_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Relationships
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey("member_profiles.id"), nullable=True)

    def as_json_dict(self):
        return {"info": self.info, "category": self.category,
            "logged_at": self.logged_at.strftime("%H:%M"), "room_number": self.room.number,
            "member_username": self.member.username}

    def __repr__(self):
        return "<Log: %s %s>" % (self.room.number, self.category)


class MemberProfile(_CRUD, db.Model):
    """
    username: A one-time-edit username just for this room.
    email: Email that should be displayed in this room.
    is_active: Indicates if this member is CURRENTLY a member of the room.
    allow_username_edit: Indicates if the username for this member has ever been set.
    """
    __tablename__ = "member_profiles"
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
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=False)
    logs = db.relationship("Log", backref="member", lazy="dynamic")

    def __repr__(self):
        return "<Member Profile: %s %s>" % (self.room.number, self.user.email)

