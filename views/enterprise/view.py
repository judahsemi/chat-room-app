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
from forms.main import CreateEnterpriseForm, EditEmployeeProfileForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url, generate_id

from .main import ent_bp



@ent_bp.route("/enterprise/new/", methods=["GET", "POST"])
@login_required
def create():
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    form = CreateEnterpriseForm()
    if request.method == "POST" and form.validate():
        enterprise = form.save(user, commit=True)
        admin_profile = EmployeeProfile.query.filter_by(user=enterprise.admin,
            enterprise=enterprise).first()
        return redirect(url_for("ent_bp.edit_employee_profile", _id=enterprise.id,
            emp_id=admin_profile.id))
    return render_template("enterprise/create.html", form=form)


@ent_bp.route("/enterprise/<_id>/dashboard/", methods=["GET"])
@login_required
def dashboard(_id):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    enterprise = Enterprise.query.get(_id)
    if not enterprise:
        return abort(404)

    return render_template("enterprise/dashboard.html", _next=_next,
        enterprise=enterprise)


@ent_bp.route("/enterprise/<_id>/emp/<emp_id>/profile/edit", methods=["GET", "POST"])
@login_required
def edit_employee_profile(_id, emp_id):
    """ """
    user = current_user
    prev, _next = navigate_url(request)

    profile = EmployeeProfile.query.get(emp_id)
    if not profile:
        return abort(404)

    form = EditEmployeeProfileForm()
    if request.method == "POST" and form.validate():
        profile = form.save(profile, commit=True)
        return redirect(url_for("ent_bp.dashboard", _id=_id))
    return render_template("enterprise/emp/edit-profile.html", form=form)

