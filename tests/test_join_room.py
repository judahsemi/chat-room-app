import re, os, shutil, time, random, requests

from flask import request, session, url_for

import unittest

import config as cfg
from config import config
from main import create_app, db
from views.socket.main import socketio
from models.main import db, User, Room, Settings, Log
from forms.main import CreateRoomForm

from utils.helper import generate_id

from .main import BaseTests, rooms_info



class JoinRoomTests(BaseTests):
    def setUp(self):
        super(JoinRoomTests, self).setUp()

        self.rooms_info = rooms_info.copy()
        self.room = CreateRoomForm(**self.rooms_info["in"]).save(
            commit=True,
            user=self.user)

    def tearDown(self):
        del self.rooms_info
        del self.room

        super(JoinRoomTests, self).tearDown()

    def test_join_room_unlogged(self):
        resp = self.unlogged_client.get(url_for("room_bp.join_room"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.login"), resp.location)

    def test_join_room(self):
        resp = self.another_client.get(url_for("room_bp.join_room"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Join", self.get_text(resp))
        self.assertIn("form", self.get_text(resp))
        self.assertIn(url_for("room_bp.logout", _external=False), self.get_text(resp))

    def test_join_room_post(self):
        resp = self.another_client.post(url_for("room_bp.join_room"),
            data={"number": self.room.number, "secret": self.room.secret})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.lounge", room=self.room), resp.location)

    def test_join_room_already_joined(self):
        resp = self.client.post(url_for("room_bp.join_room"),
            data={"number": self.room.number, "secret": self.room.secret},
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("already joined this room", self.get_text(resp))
        self.assertIn("Lounge", self.get_text(resp))

    def test_join_room_post_bad_auth(self):
        resp = self.another_client.post(url_for("room_bp.join_room"),
            data={"number": time.time(), "secret": os.urandom(8)})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("not find this room", self.get_text(resp))
        self.assertIn("Join", self.get_text(resp))

    def test_join_room_post_bad_auth_2(self):
        resp = self.another_client.post(url_for("room_bp.join_room"),
            data={"number": self.room.number, "secret": os.urandom(8)})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("not find this room", self.get_text(resp))
        self.assertIn("Join", self.get_text(resp))

    def test_join_room_post_bad_auth_3(self):
        resp = self.another_client.post(url_for("room_bp.join_room"),
            data={"number": time.time(), "secret": self.room.secret})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("not find this room", self.get_text(resp))
        self.assertIn("Join", self.get_text(resp))

