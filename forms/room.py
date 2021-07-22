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
            is_active=True,
            user=user,
            room=room).add(commit=commit)
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
        memb_profile = room.members.filter_by(user=user).first()
        if not memb_profile:
            memb_profile = MemberProfile(
                username=user.def_username,
                is_active=True,
                user=user,
                room=room,
                **kwargs).add(commit=commit)
        memb_profile.update(is_active=True, commit=commit)

        if not memb_profile.allow_username_edit:
            log = Log(
                info="{} joined this room".format(memb_profile.username),
                category=cfg.LogConstant.CAT_ROOM,
                room=memb_profile.room,
                member=memb_profile).add(commit=commit)
            print(">>>", log.info, log.room.number, flush=True)
            send(log.clean_json(), to=str(log.room.number), namespace="/room-chat")
        return memb_profile


class EditRoomUsernameForm(FlaskForm):
    username = wtforms.StringField(
        "Username",
        validators=[validators.DataRequired()])

    display = ["username"]

    def save(self, memb_profile, commit=True):
        memb_profile.update(
            username=self.username.data,
            allow_username_edit=False,
            commit=commit)

        if memb_profile.user == memb_profile.room.admin:
            info = "{} created this room".format(memb_profile.username)
            memb_profile.room.update(is_active=True, commit=True)
        else:
            info = "{} joined this room".format(memb_profile.username)

        log = Log(
            info=info,
            category=cfg.LogConstant.CAT_ROOM,
            room=memb_profile.room,
            member=memb_profile).add(commit=commit)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.clean_json(), to=str(log.room.number), namespace="/room-chat")
        return memb_profile


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
        memb_profile.is_active = False
        memb_profile.save(commit=commit)

        log = Log(
            info="{} left this room".format(memb_profile.username),
            category=cfg.LogConstant.CAT_ROOM,
            room=memb_profile.room,
            member=memb_profile).add(commit=commit)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.clean_json(), to=str(log.room.number), namespace="/room-chat")
        return memb_profile


class DeleteRoomForm(FlaskForm):
    display = []

    def save(self, admin_profile, commit=True):
        room = admin_profile.room
        for memb in room.members:
            if memb == admin_profile:
                continue

            memb.delete(commit=False)

            log = Log(
                info="{} removed {} from this room".format(admin_profile.username, memb.username),
                category=cfg.LogConstant.CAT_ROOM,
                room=room,
                member=memb).add(commit=commit)
            print(">>>", log.info, log.room.number, flush=True)
            send(log.clean_json(), to=str(log.room.number), namespace="/room-chat")
        admin_profile.delete(commit=False)

        for log in room.logs:
            log.delete(commit=False)
        room.delete(commit=commit)
        return room

