import datetime, shutil, time

import wtforms
from wtforms import validators, ValidationError
from flask_wtf import FlaskForm
from flask_socketio import SocketIO, send, emit

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log, MemberProfile

from utils.helper import generate_slug, generate_id



class CreateRoomForm(FlaskForm):
    topic = wtforms.StringField(
        "Topic",
        validators=[validators.DataRequired(), validators.Length(min=4, max=32)])
    kind = wtforms.SelectField(
        "Type",
        choices=(
            (cfg.RoomConstant.KIND_OPEN, "Public"),
            (cfg.RoomConstant.KIND_CLOSE, "Private")),
        coerce=int,
        validators=[validators.InputRequired()])

    display = ["topic", "kind"]

    def save(self, user, commit=True, **kwargs):
        """ Create a new room and a member profile for the admin """
        settings = Settings().add(commit=False)
        room = Room(
            topic=self.topic.data,
            kind=self.kind.data,
            settings=settings,
            admin=user,
            **kwargs).add(commit=commit)
        if not commit:
            return room

        memb_profile = MemberProfile(
            username=user.def_username,
            is_active=True,
            allow_username_edit=True,
            user=user,
            room=room).add(commit=True)
        return room


class JoinRoomForm(FlaskForm):
    number = wtforms.StringField(
        "Room Number",
        validators=[validators.DataRequired()])
    password = wtforms.StringField(
        "Room Pass",
        validators=[])

    display = ["number", "password"]

    def validate_number(self, number):
        room = Room.query.filter_by(number=number.data, is_active=True).first()
        if not room:
            raise ValidationError("Could not find this room.")

    def validate_password(self, password):
        room = Room.query.filter_by(number=self.number.data, is_active=True).first()
        if room and room.password_hash and not room.verify_password(password.data):
            raise ValidationError("Invalid password. Contact room admin.")

    def save(self, room, user, commit=True, **kwargs):
        """ Create or activate a member profile and add it to the room if it's new """
        memb_profile = room.members.filter_by(user=user).first()
        if not memb_profile:
            memb_profile = MemberProfile(
                username=user.def_username,
                is_active=True,
                allow_username_edit=True,
                user=user,
                room=room,
                **kwargs).add(commit=commit)
            if not commit:
                return memb_profile

        memb_profile.update(is_active=True, commit=True)
        if not memb_profile.allow_username_edit:
            log = Log(
                info="{} joined this room".format(memb_profile.username),
                category=cfg.LogConstant.CAT_ROOM,
                room=memb_profile.room,
                member=memb_profile).add(commit=True)
            print(">>>", log.info, log.room.number, flush=True)
            send(log.as_json_dict(), to=log.room.number, namespace="/room-chat")
        return memb_profile


class EditRoomUsernameForm(FlaskForm):
    username = wtforms.StringField(
        "Username",
        validators=[validators.DataRequired(), validators.Length(min=4, max=25)])

    display = ["username"]

    def __init__(self, memb_profile, data={}, *args, **kwargs):
        self.memb_profile = memb_profile

        data["username"] = memb_profile.username
        super(EditRoomUsernameForm, self).__init__(data=data, *args, **kwargs)

    def validate_username(self, username):
        profile = self.memb_profile.room.members.filter_by(username=username.data).first()
        if profile and profile != self.memb_profile:
            raise ValidationError("This username has already been taken.")

        user = User.query.filter_by(def_username=username.data).first()
        if user and user != self.memb_profile.user:
            raise ValidationError("This username is not available.")

    def save(self, memb_profile, commit=True):
        memb_profile.update(
            username=self.username.data,
            allow_username_edit=False,
            commit=commit)
        if not commit:
            return memb_profile

        if memb_profile.user == memb_profile.room.admin:
            info = "{} created this room".format(memb_profile.username)
            memb_profile.room.update(is_active=True, commit=True)
        else:
            info = "{} joined this room".format(memb_profile.username)

        log = Log(
            info=info,
            category=cfg.LogConstant.CAT_ROOM,
            room=memb_profile.room,
            member=memb_profile).add(commit=True)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.as_json_dict(), to=log.room.number, namespace="/room-chat")
        return memb_profile


class RoomMessageForm(FlaskForm):
    message = wtforms.StringField(
        "Message",
        validators=[validators.DataRequired()])

    display = ["message"]

    def save(self, memb_profile, commit=True, **kwargs):
        log = Log(
            info=self.message.data,
            category=cfg.LogConstant.CAT_CHAT,
            room=room,
            member=memb_profile,
            **kwargs).add(commit=True)
        return log


class LeaveRoomForm(FlaskForm):
    display = []

    def save(self, memb_profile, commit=True):
        """ De-activate a room-member profile """
        memb_profile.update(is_active=False, commit=commit)
        if not commit:
            return memb_profile

        log = Log(
            info="{} left this room".format(memb_profile.username),
            category=cfg.LogConstant.CAT_ROOM,
            room=memb_profile.room,
            member=memb_profile).add(commit=True)
        print(">>>", log.info, log.room.number, flush=True)
        send(log.as_json_dict(), to=log.room.number, namespace="/room-chat")
        return memb_profile


class DeleteRoomForm(FlaskForm):
    display = []

    def save(self, admin_profile, commit=True):
        """ Delete room, it members and logs """
        room = admin_profile.room
        for memb in room.members:
            if memb == admin_profile:
                continue

            memb.delete(commit=False)

            log = Log(
                info="{} removed {} from this room".format(admin_profile.username, memb.username),
                category=cfg.LogConstant.CAT_ROOM,
                room=room,
                member=memb).add(commit=True)
            print(">>>", log.info, log.room.number, flush=True)
            send(log.as_json_dict(), to=log.room.number, namespace="/room-chat")
        admin_profile.delete(commit=False)

        for log in room.logs:
            log.delete(commit=False)
        room.delete(commit=True)
        return room

