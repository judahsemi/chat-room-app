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
from models.main import db, User, Room, Settings, Log, MemberProfile
from forms.main import CreateRoomForm, JoinRoomForm, FirstTimeGuestForm, RoomMessageForm
from forms.main import LeaveRoomForm, DeleteRoomForm, BlankForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url, generate_id

from .main import room_bp



@room_bp.route("/rooms/joined/", methods=["GET"])
@login_required
def joined_list():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profiles = user.get_active("memb_profiles").all()
    return render_template("room/joined-list.html", memb_profiles=memb_profiles)


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
        room = Room.query.filter_by(number=form.number.data).first()
        if room:
            if room.get_active("members").filter_by(user=user).first():
                flash("You have already joined this room")
                return redirect(url_for("room_bp.lounge", room=room))

            memb_profile = form.save(room, user, commit=True)
            return redirect(url_for("room_bp.lounge", room=room))

        flash("Could not find this room.")
    return render_template("room/join.html", form=form)


@room_bp.route("/room/<real_room:room>/lounge/", methods=["GET", "POST"])
@login_required
def lounge(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)
    
    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("user_bp.dashboard"))
    return render_template("room/lounge.html", memb_profile=memb_profile)


@room_bp.route("/room/<real_room:room>/", methods=["GET"])
@login_required
def room(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("user_bp.dashboard"))

    form = RoomMessageForm()
    logs = room.logs.all()
    return render_template("room/room.html", form=form, logs=logs, room=room,
        memb_profile=memb_profile)


@room_bp.route("/room/<real_room:room>/leave/", methods=["GET", "POST"])
@login_required
def leave_room(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("user_bp.dashboard"))

    form = BlankForm()
    if request.method == "POST" and form.validate():
        memb_profile = LeaveRoomForm().save(memb_profile, commit=True)
        return redirect(url_for("room_bp.joined_list"))

    params = {}
    params["action"] = "leave"
    params["object"] = "room"
    params["next"] = request.url
    params["this"] = url_for("room_bp.lounge", room=room, _external=True)
    params["prev"] = prev or url_for("room_bp.lounge", room=room, _external=True)
    return render_template("confirm-action.html", form=form, **params)


@room_bp.route("/room/<real_room:room>/delete/", methods=["GET", "POST"])
@login_required
def delete_room(room):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.")
        return redirect(prev or url_for("user_bp.dashboard"))

    if room.admin != current_user:
        flash("You are not authorized to perform this action.")
        return redirect(prev or url_for("room_bp.lounge", room=room))

    form = BlankForm()
    if request.method == "POST" and form.validate():
        room = DeleteRoomForm().save(room, commit=True)
        return redirect(url_for("room_bp.joined_list"))

    params = {}
    params["action"] = "delete"
    params["object"] = "room"
    params["next"] = request.url
    params["this"] = url_for("room_bp.lounge", room=room, _external=True)
    params["prev"] = prev or url_for("room_bp.lounge", room=room, _external=True)
    return render_template("confirm-action.html", form=form, **params)

