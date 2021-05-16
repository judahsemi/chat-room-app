import datetime, random, time

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

from utils.helper import generate_slug, generate_id

import config as cfg
from config import config
from .main import db
from .main import _CRUD, Protected, login_manager



members = db.Table("members",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("room_id", db.Integer, db.ForeignKey("rooms.id")),)


class Room(_CRUD, db.Model):
    """ """
    __tablename__ = "rooms"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False, unique=True)
    secret = db.Column(db.String(32), default=None)
    topic = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    last_modified = db.Column(db.DateTime, default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow)

    # Relationships
    admin_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    settings_id = db.Column(db.Integer, db.ForeignKey("settings.id"), nullable=False)
    members = db.relationship("User", secondary=members,
        backref=db.backref("joined_rooms", lazy="dynamic"), lazy="dynamic")
    logs = db.relationship("Log", backref="room", lazy="dynamic")

    def __init__(self, **kwargs):
        kwargs["number"], kwargs["secret"] = self.generate_auth()
        
        super(Room, self).__init__(**kwargs)

    def generate_auth(self):
        number = random.randint(cfg.RoomConstant.NUM_LOWER_LIMIT,
            cfg.RoomConstant.NUM_UPPER_LIMIT)
        
        while self.query.filter_by(number=number).first():
            number = random.randint(cfg.RoomConstant.NUM_LOWER_LIMIT,
                cfg.RoomConstant.NUM_UPPER_LIMIT)

        secret = generate_id(time.time(), 16, keylen=4)
        return number, secret

    def get_user_username(self, user):
        logs = user.logs.filter_by(room=self).all()
        for log in logs:
            if log.username:
                return log.username
        return None

    def get_user_with_username(self, username):
        logs = self.log.filter_by(username=username).all()
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

