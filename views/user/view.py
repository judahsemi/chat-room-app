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
from models.main import db, User, Room, MemberProfile, Notification
from forms.main import CreateRoomForm, JoinRoomForm, EditRoomUsernameForm, RoomMessageForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url, generate_id

from .main import user_bp



@user_bp.route("/", methods=["GET"])
def index():
    """ The landing page """
    params = {}
    user = current_user
    prev, _next = navigate_url(request)

    admin_user = User.query.filter_by(def_username="admin").first()
    params["rec_rooms"] = Room.recommended(admin_user, topk=10)
    params["new_rooms"] = Room.newest(topk=10)
    params["pop_rooms"] = Room.popular(topk=10)
    params["active_rooms"] = Room.most_active(topk=10)
    return render_template("user/index.html", **params)


@user_bp.route("/dashboard/", methods=["GET"])
@login_required
def dashboard():
    """ User dashboard """
    user = current_user
    prev, _next = navigate_url(request)

    memb_profiles = user.get_active("memb_profiles").all()
    return render_template("user/dashboard.html", _next=_next,
        memb_profiles=memb_profiles)


@user_bp.route("/notifications/", methods=["GET"])
@login_required
def list_notifications():
    """ List user notifications """
    user = current_user
    prev, _next = navigate_url(request)

    notifications = user.notifications.all()
    return render_template("user/notifications.html", _next=_next,
        notifications=notifications)


@user_bp.route("/notifications/<nid>/delete", methods=["GET"])
@login_required
def delete_notification(nid):
    """ Delete a notification """
    user = current_user
    prev, _next = navigate_url(request)

    notification = user.notifications.filter_by(id=nid).first()
    if notification:
        flash("Deleted successfully.", "success")
        notification.delete(commit=True)
    return redirect(url_for("user_bp.list_notifications"))


@user_bp.route("/settings/", methods=["GET"])
@login_required
def settings():
    """ View and edit settings """
    user = current_user
    prev, _next = navigate_url(request)

    return render_template("user/settings.html", _next=_next, user=user)

