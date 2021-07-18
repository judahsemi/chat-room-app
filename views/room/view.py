import os, time, requests

from flask import Flask, Blueprint
from flask import request, session, url_for
from flask import jsonify, make_response, redirect, abort
from flask import render_template, flash
# from flask import current_app, g, request, session
# from flask import request_finished, send_from_directory
from flask_login import login_required, current_user

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log, Enterprise, EmployeeProfile
from forms.main import CreateRoomForm, JoinRoomForm, FirstTimeGuestForm, RoomMessageForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url, generate_id

from .main import room_bp



@room_bp.route("/", methods=["GET"])
def index():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    return render_template("user/index.html")


@room_bp.route("/dashboard/", methods=["GET"])
@login_required
def dashboard():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    joined_rooms = []#user.joined_rooms.all()
    emp_profiles = EmployeeProfile.query.filter_by(user=user).all()
    enterprises = Enterprise.query.filter(EmployeeProfile.user == user).all()
    return render_template("user/dashboard.html", _next=_next, joined_rooms=joined_rooms,
        emp_profiles=emp_profiles, enterprises=enterprises)


@room_bp.route("/rooms/create/", methods=["GET", "POST"])
@login_required
def create_room():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    form = CreateRoomForm()
    if request.method == "POST" and form.validate():
        room = form.save(user, commit=True)
        return redirect(url_for("room_bp.lounge", room=room))
    return render_template("room/create.html", form=form)


@room_bp.route("/rooms/join/", methods=["GET", "POST"])
@login_required
def join_room():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    form = JoinRoomForm()
    if request.method == "POST" and form.validate():
        room = Room.find(form.number.data, form.secret.data)
        if room:
            if user in room.members.all():
                flash("You have already joined this room")
                return redirect(url_for("room_bp.lounge", room=room))

            room = form.save(room, user, commit=True)
            return redirect(url_for("room_bp.lounge", room=room))

        flash("Could not find this room.")
    return render_template("room/join.html", form=form)


@room_bp.route("/room/<real_room:room>/lounge/", methods=["GET", "POST"])
@login_required
def lounge(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)
    
    if user not in room.members.all():
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("room_bp.dashboard"))

    username = room.get_user_username(user)
    form = FirstTimeGuestForm(username=username)
    if request.method == "POST":
        if not username and form.validate():
            username = form.save(room, user, commit=True)

        if username:
            session["username"] = username
            return redirect(url_for("room_bp.room", room=room))
    return render_template("room/lounge.html", form=form, room=room,
        username=username)


@room_bp.route("/room/<real_room:room>/", methods=["GET"])
@login_required
def room(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    if user not in room.members.all():
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("room_bp.dashboard"))

    username = room.get_user_username(user)
    if not username:
        flash("You need to have confirmed your details here.")
        return redirect(url_for("room_bp.lounge", room=room))

    form = RoomMessageForm()
    logs = [log.clean_json() for log in room.logs.all()]

    user = user
    session["username"] = username
    return render_template("room/room.html", form=form, logs=logs, room=room, user=user,
        username=username)

