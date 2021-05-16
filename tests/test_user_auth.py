import re, os, shutil, time, random, requests

from flask import request, session, url_for

import unittest

import config as cfg
from config import config
from main import create_app, db
from views.socket.main import socketio
from models.main import db, User, Room, Settings, Log
from forms.main import RegisterForm, LoginForm

from utils.helper import generate_id

from .main import BaseTests



class UserAuthTests(BaseTests):
    def test_register(self):
        resp = self.unlogged_client.get(url_for("room_bp.register"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Register", resp.get_data(as_text=True))
        self.assertIn(url_for("room_bp.login", _external=False), self.get_text(resp))

    def test_register_post(self):
        resp = self.unlogged_client.post(url_for("room_bp.register"),
            data=self.users_info["out"]["register"])
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.dashboard"), resp.location)

    def test_login(self):
        resp = self.unlogged_client.post(url_for("room_bp.login"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Login", resp.get_data(as_text=True))
        self.assertIn(url_for("room_bp.register", _external=False), self.get_text(resp))

    def test_login_post(self):
        resp = self.unlogged_client.post(url_for("room_bp.login"),
            data=self.users_info["in"]["login"])
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.dashboard"), resp.location)

    def test_logout(self):
        resp = self.client.get(url_for("room_bp.logout"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.login"), resp.location)

    def test_all_three(self):
        resp = self.unlogged_client.post(url_for("room_bp.register"),
            data=self.users_info["out"]["register"], follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("successful", self.get_text(resp))

        resp = self.unlogged_client.get(url_for("room_bp.logout"), follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("logged out", self.get_text(resp))

        resp = self.unlogged_client.post(url_for("room_bp.login"),
            data=self.users_info["out"]["login"], follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(url_for("room_bp.logout", _external=False), self.get_text(resp))

        resp = self.unlogged_client.get(url_for("room_bp.logout"), follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("logged out", self.get_text(resp))

