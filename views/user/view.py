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

from .main import user_bp



@user_bp.route("/", methods=["GET"])
def index():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    return render_template("user/index.html")


@user_bp.route("/dashboard/", methods=["GET"])
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

