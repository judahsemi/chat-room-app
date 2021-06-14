import os, time, random

from flask import Flask, Blueprint
from flask import request, session, url_for
from flask import jsonify, make_response, redirect, abort
from flask import render_template, flash
# from flask import current_app, g, request, session
# from flask import request_finished, send_from_directory
from flask_login import login_required, current_user

import config as cfg
from config import config
from models.main import db, User
from views.socket.main import socketio
# from forms.view import RegisterForm, LoginForm

# from utils.html_object import HtmlTableView
from utils.helper import navigate_url

from main import create_app



app = create_app(os.environ.get("CONFIG_NAME") or "default")



if __name__ == "__main__":
    
    db.create_all(app=app)
    socketio.run(app)

