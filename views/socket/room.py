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
from models.main import db, User, Room, Settings, Log
from forms.main import FirstTimeGuestForm, RoomMessageForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url

from .main import socketio



@socketio.on("entered")
def entered(data):
    result = validate_request(data)
    if not result:
        print(">>>", "Couldn't join room", flush=True)
        send("An error occurred")
        return None
    
    room = result["room"]
    print(">>>", "Joining room", flush=True)
    join_room(str(room.number))


@socketio.on("message")
def receive_message(data, msg):
    result = validate_request(data)
    if not result:
        print(">>>", "Couldn't join room", flush=True)
        send("An error occurred")
        return None

    log = Log(
        info=msg,
        category=cfg.LogConstant.CAT_CHAT,
        username=result["username"],
        room=result["room"],
        user=result["user"]).add(commit=True)

    ret_json = log.clean_json()
    ret_json["logged_at"] = str(ret_json.get("logged_at").strftime("%H:%M"))
    print(">>>", "Sending message to the entire room", flush=True)
    send(ret_json, to=str(log.room.number))


def validate_request(data):
    # print("#"*10, data, flush=True)
    try:
        data["number"] = int(data["number"])
    except:
        return False

    room = Room.find(data["number"], data["secret"])
    if not room:
        print(">>>", "Could not find the room", flush=True)
        return False

    user = room.get_user_with_username(data["username"])
    if (not user) or (user not in room.members) or (user != current_user):
        print(">>>", "Not authorized", flush=True)
        return False

    print(">>>", "Request validated", flush=True)
    result = {"user": user, "room": room, "username": data["username"]}
    return result


@socketio.on("connect")
def connect():
    print(">>>", "Client connected", flush=True)


@socketio.on("disconnect")
def disconnect():
    print(">>>", "Client disconnected", flush=True)

