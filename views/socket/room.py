import os, time, requests

from flask import Flask, Blueprint
from flask import request, session, url_for
from flask import jsonify, make_response, redirect, abort
from flask import render_template, flash
# from flask import current_app, g, request, session
# from flask import request_finished, send_from_directory
from flask_login import login_required, current_user
from flask_socketio import SocketIO, ConnectionRefusedError, disconnect, send, emit
from flask_socketio import join_room, leave_room, close_room, rooms

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log, MemberProfile
from forms.main import EditRoomUsernameForm, RoomMessageForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url

from .main import socketio



@socketio.on("entered", namespace="/room-chat")
def entered(data):
    """ Add user to a room socket """
    result = validate_request(data)
    if not result:
        print(">>>", "Couldn't join room", flush=True)
        send("An error occurred")
        return None
    
    profile = result["profile"]
    print(">>>", "Joining room", flush=True)
    join_room(profile.room.number)


@socketio.on("message", namespace="/room-chat")
def receive_message(data, msg):
    """ Receive sent messages and broadcast to the entire room """
    result = validate_request(data)
    if not result:
        print(">>>", "Couldn't join room", flush=True)
        send("An error occurred")
        return None

    profile = result["profile"]
    log = Log(
        info=msg,
        category=cfg.LogConstant.CAT_CHAT,
        room=profile.room,
        member=profile).add(commit=True)
    print(">>>", "Sending message to the entire room", log.room.number, flush=True)
    send(log.as_json_dict(), to=log.room.number)


def validate_request(data):
    """ Check if the request can be trusted """
    print("#"*10, data, flush=True)
    room = Room.query.filter_by(number=data["number"]).first()
    profile = MemberProfile.query.filter_by(username=data["username"], room=room).first()
    if not profile:
        return False

    print(">>>", "Request validated", flush=True)
    result = {"profile": profile}
    return result


@socketio.on("connect", namespace="/room-chat")
def connect():
    """ Connect event for a room chat """
    print(">>>", "Client connected to namespace: '/room-chat'", flush=True)


@socketio.on("disconnect", namespace="/room-chat")
def disconnect():
    """ Disconnect event for a room chat """
    print(">>>", "Client disconnected from namespace: '/room-chat'", flush=True)

