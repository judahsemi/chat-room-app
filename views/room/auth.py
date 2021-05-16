import os, time

from flask import Flask, Blueprint
from flask import request, session, url_for
from flask import jsonify, make_response, redirect, abort
from flask import render_template, flash
# from flask import current_app, g, request, session
# from flask import request_finished, send_from_directory
from flask_login import login_required, login_user, logout_user

import config as cfg
from config import config
from models.main import db, User, Room, Settings, Log
from forms.main import RegisterForm, LoginForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url

from .main import room_bp



@room_bp.route("/auth/register", methods=["GET", "POST"])
def register():
    prev, _next = navigate_url(request)
    
    form = RegisterForm()
    if request.method == "POST" and form.validate():
        user = form.save(commit=True)
        login_user(user, remember=bool(request.form.get("remember")))

        flash("Registration successful")
        return redirect(prev or url_for("room_bp.dashboard"))
    return render_template("user/register.html", form=form, _next=prev)


@room_bp.route("/auth/login", methods=["GET", "POST"])
def login():
    prev, _next = navigate_url(request)
    
    form = LoginForm()
    if request.method == "POST" and form.validate():
        user = User.authenticate(
            User.email == form.email.data, password=form.password.data)
        if user:
            login_user(user, remember=bool(request.form.get("remember")))
            return redirect(prev or url_for("room_bp.dashboard"))

        flash("Invalid Login Credentials")
    return render_template("user/login.html", form=form, _next=prev)


@room_bp.route("/auth/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    flash("You have logged out successfully")
    return redirect(url_for("room_bp.login"))

