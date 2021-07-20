import datetime, shutil, time

import wtforms
from wtforms import validators
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, send, emit

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log, MemberProfile

from utils.helper import generate_slug, generate_id



class CreateRoomForm(FlaskForm):
    topic = wtforms.StringField(
        "Topic",
        validators=[validators.DataRequired()])
    kind = wtforms.SelectField(
        "Type",
        choices=(
            (cfg.RoomConstant.KIND_OPEN, "Public"),
            (cfg.RoomConstant.KIND_CLOSE, "Private")),
        coerce=int,
        validators=[validators.DataRequired()])

    display = ["topic", "kind"]

    def save(self, user, commit=True, **kwargs):
        settings = Settings().add(commit=False)
        room = Room(
            topic=self.topic.data,
            kind=self.kind.data,
            settings=settings,
            admin=user,
            **kwargs).add(commit=commit)

        memb_profile = MemberProfile(
            username=user.def_username,
            user=user,
            room=room).add(commit=commit)

        log = Log(
            info="Admin created and joined this room",
            category=cfg.LogConstant.CAT_ROOM,
            room=room,
            member=memb_profile).add(commit=commit)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.clean_json(), to=str(log.room.number), namespace="/chat")
        return room


class JoinRoomForm(FlaskForm):
    number = wtforms.StringField(
        "Room Number",
        validators=[validators.DataRequired()])
    password = wtforms.StringField(
        "Room Pass",
        validators=[])

    display = ["number", "password"]

    def save(self, room, user, commit=True, **kwargs):
        memb_profile = MemberProfile(
            username=user.def_username,
            user=user,
            room=room,
            **kwargs).add(commit=commit)

        log = Log(
            info="Someone joined this room",
            category=cfg.LogConstant.CAT_ROOM,
            room=room,
            member=memb_profile).add(commit=commit)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.clean_json(), to=str(log.room.number), namespace="/chat")
        return memb_profile


class FirstTimeGuestForm(FlaskForm):
    username = wtforms.StringField(
        "Username",
        validators=[validators.DataRequired()])

    display = ["username"]

    def save(self, room, user, commit=True, **kwargs):
        log = Log(
            info="{} is entering this room for the first time".format(self.username.data),
            category=cfg.LogConstant.CAT_ROOM,
            username=self.username.data,
            room=room,
            user=user,
            **kwargs).add(commit=commit)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.clean_json(), to=str(log.room.number), namespace="/chat")
        return self.username.data


class RoomMessageForm(FlaskForm):
    message = wtforms.StringField(
        "Message",
        validators=[validators.DataRequired()])

    display = ["message"]

    def save(self, room, user, username, commit=True, **kwargs):
        log = Log(
            info=self.message.data,
            category=cfg.LogConstant.CAT_CHAT,
            username=username,
            room=room,
            user=user,
            **kwargs).add(commit=commit)
        return log


class LeaveRoomForm(FlaskForm):
    display = []

    def save(self, memb_profile, commit=True):
        memb_profile.delete(commit=commit)
        return memb_profile


class DeleteRoomForm(FlaskForm):
    display = []

    def save(self, room, commit=True):
        for memb in room.members:
            LeaveRoomForm().save(memb, commit=False)

        for log in room.logs:
            log.delete(commit=False)
        room.delete(commit=commit)
        return room

