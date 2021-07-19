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
from forms.main import FirstTimeGuestForm, RoomMessageForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url

from .main import socketio



@socketio.on("entered", namespace="/room-chat")
def entered(data):
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
    print("#"*20, log.as_dict(), flush=True)

    ret_json = log.clean_json()
    ret_json["logged_at"] = str(ret_json.get("logged_at").strftime("%H:%M"))
    ret_json["sender_username"] = profile.username
    print(">>>", "Sending message to the entire room", flush=True)
    send(ret_json, to=str(log.room.number))


def validate_request(data):
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
    print(">>>", "Client connected to namespace: '/room-chat'", flush=True)


@socketio.on("disconnect", namespace="/room-chat")
def disconnect():
    print(">>>", "Client disconnected from namespace: '/room-chat'", flush=True)

