import re, os, shutil, time, random

import uuid
from werkzeug import security
from werkzeug.utils import secure_filename
from werkzeug.routing import BaseConverter, ValidationError

import config as cfg
from config import Config
from models.main import db, User, Room, Settings, Log



class RealRoom(BaseConverter):
    """ Raise error if room does not exist """
    def to_python(self, room):
        """ room should be the room id """
        try:
            room_id = int(room)
            room = Room.query.get(room_id)
            if room:
                return room
        except:
            pass
        raise ValidationError()

    def to_url(self, room):
        """ room should be the actual room model """
        if isinstance(room, Room) and hasattr(room, "id"):
            return str(room.id)
        raise ValidationError()

