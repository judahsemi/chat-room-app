import datetime

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# from utils.helper import generate_slug

import config as cfg
from config import config
from main import db
from main import login_manager



class Protected:
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        if hasattr(self, "password_hash"):
            return check_password_hash(self.password_hash, password)
        raise NotImplemented

    @classmethod
    def authenticate(cls, condition, password):
        obj = cls.query.filter(condition).first()
        if obj and obj.verify_password(password):
            return obj
        return False


class _CRUD:
    def update(self, *, commit=True, **kwargs):
        for attr in kwargs:
            if hasattr(self, attr) or hasattr(self.__class__, attr):
                setattr(self, attr, kwargs.get(attr))
        return self.save(commit=commit)

    def add(self, commit=True):
        db.session.add(self)
        return self.save(commit=commit)

    def delete(self, commit=True):
        db.session.delete(self)
        return self.save(commit=commit)

    def save(self, commit=True):
        if commit:
            db.session.commit()
        return self

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def get_active(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr).filter_by(is_active=True)
        raise Exception


from .account import User, Notification
from .room import Room, Settings, Log, MemberProfile
from .session import Session, Rule, Record, ParticipantProfile

