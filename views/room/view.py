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
from models.main import db, User, Notification, Room, Settings, Log, MemberProfile
from forms.main import CreateRoomForm, JoinRoomForm, EditRoomUsernameForm, RoomMessageForm
from forms.main import SendRoomInviteForm, LeaveRoomForm, DeleteRoomForm, BlankForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url, generate_id

from .main import room_bp



@room_bp.route("/rooms/joined/", methods=["GET"])
@login_required
def joined_list():
    """ List of rooms that user is currently in """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profiles = user.get_active("memb_profiles").all()
    return render_template("room/joined-list.html", memb_profiles=memb_profiles)


@room_bp.route("/rooms/create/", methods=["GET", "POST"])
@login_required
def create_room():
    """ Create a new room """
    user = current_user
    prev, _next = navigate_url(request)

    form = CreateRoomForm()
    if request.method == "POST" and form.validate():
        room = form.save(user, commit=True)
        flash("Created successfully.", "success")
        return redirect(url_for("room_bp.lounge", room=room))
    return render_template("room/create.html", form=form)


@room_bp.route("/rooms/join/", methods=["GET", "POST"])
@login_required
def join_room():
    """ Join a fully-created room """
    user = current_user
    prev, _next = navigate_url(request)

    form = JoinRoomForm()
    if request.method == "POST" and form.validate():
        room = Room.query.filter_by(number=form.number.data, is_active=True).first()
        if room:
            if room.get_active("members").filter_by(user=user).first():
                flash("You have already joined this room.", success="message")
                return redirect(url_for("room_bp.lounge", room=room))

            memb_profile = form.save(room, user, commit=True)
            flash("Joined successfully.", "success")
            return redirect(url_for("room_bp.lounge", room=room))
    return render_template("room/join.html", form=form)


@room_bp.route("/rooms/join/link", methods=["GET"])
@login_required
def join_room_via_link():
    """ Join a fully-created room via link """
    user = current_user
    prev, _next = navigate_url(request)

    room = Room.validate_join_token(request.args.get("token"))
    if room:
        if room.get_active("members").filter_by(user=user).first():
            flash("You have already joined this room.", success="message")
            return redirect(url_for("room_bp.lounge", room=room))

        memb_profile = JoinRoomForm().save(room, user, commit=True)
        flash("Joined successfully.", "success")
        return redirect(url_for("room_bp.lounge", room=room))
    flash("This link is not valid. Try again later with a new one.", "error")
    return redirect(prev or url_for("user_bp.index"))


@room_bp.route("/room/<real_room:room>/invite", methods=["GET"])
@login_required
def send_room_invite(room):
    """ Invite another user to this room """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.", "error")
        return redirect(prev or url_for("user_bp.dashboard"))

    re_username = request.args.get("username")
    receiver = User.query.filter_by(def_username=re_username).first()
    if not receiver:
        flash("User with username '{}' does not exist.".format(re_username), "error")
        return redirect(prev or url_for("room_bp.room", room=room))

    if room.get_active("members").filter_by(user=receiver).first():
        flash("User has already joined this room.", "error")
        return redirect(prev or url_for("room_bp.room", room=room))

    invite_link = url_for("room_bp.join_room_via_link", token=room.generate_join_token())

    note = SendRoomInviteForm().save(memb_profile, receiver, invite_link, commit=True)
    flash("Invite sent.", "success")
    return redirect(prev or url_for("room_bp.room", room=room))


@room_bp.route("/room/<real_room:room>/lounge/", methods=["GET", "POST"])
@login_required
def lounge(room):
    """ Shows room info; available to only members """
    user = current_user
    prev, _next = navigate_url(request)
    
    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.", "error")
        return redirect(prev or url_for("user_bp.dashboard"))

    form = EditRoomUsernameForm(memb_profile) if memb_profile.allow_username_edit else None
    if request.method == "POST" and form.validate():
        memb_profile = form.save(memb_profile, commit=True)
        return redirect(url_for("room_bp.lounge", room=room))
    return render_template("room/lounge.html", form=form, memb_profile=memb_profile)


@room_bp.route("/room/<real_room:room>/", methods=["GET"])
@login_required
def room(room):
    """ View of the actual room """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.", "error")
        return redirect(prev or url_for("user_bp.dashboard"))

    if memb_profile.allow_username_edit:
        flash("You are to fill your username before entering.", "error")
        return redirect(prev or url_for("room_bp.lounge", room=room))

    form = RoomMessageForm()
    logs = room.logs.all()
    return render_template("room/room.html", form=form, logs=logs, room=room,
        memb_profile=memb_profile)


@room_bp.route("/room/<real_room:room>/leave/", methods=["GET", "POST"])
@login_required
def leave_room(room):
    """ Leave a room user is currently in """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.", "error")
        return redirect(prev or url_for("user_bp.dashboard"))

    form = BlankForm()
    if request.method == "POST" and form.validate():
        memb_profile = LeaveRoomForm().save(memb_profile, commit=True)
        flash("Left successfully.", "success")
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
    """ Delete a room user own """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profile = room.get_active("members").filter_by(user=user).first()
    if not memb_profile:
        flash("You have not yet joined this room.", "error")
        return redirect(prev or url_for("user_bp.dashboard"))

    if room.admin != current_user:
        flash("You are not authorized to perform this action.", "error")
        return redirect(prev or url_for("room_bp.lounge", room=room))

    form = BlankForm()
    if request.method == "POST" and form.validate():
        room = DeleteRoomForm().save(memb_profile, commit=True)
        flash("Deleted successfully.", "success")
        return redirect(url_for("room_bp.joined_list"))

    params = {}
    params["action"] = "delete"
    params["object"] = "room"
    params["next"] = request.url
    params["this"] = url_for("room_bp.lounge", room=room, _external=True)
    params["prev"] = prev or url_for("room_bp.lounge", room=room, _external=True)
    return render_template("confirm-action.html", form=form, **params)

