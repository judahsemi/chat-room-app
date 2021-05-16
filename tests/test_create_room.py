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



class CreateRoomTests(BaseTests):
    def setUp(self):
        super(CreateRoomTests, self).setUp()

        self.rooms_info = rooms_info.copy()
        self.room = CreateRoomForm(**self.rooms_info["in"]).save(
            commit=True,
            user=self.user)

    def tearDown(self):
        del self.rooms_info
        del self.room

        super(CreateRoomTests, self).tearDown()

    def test_create_room_unlogged(self):
        resp = self.unlogged_client.get(url_for("room_bp.create_room"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.login"), resp.location)

    def test_create_room(self):
        resp = self.client.get(url_for("room_bp.create_room"))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Create", self.get_text(resp))
        self.assertIn("form", self.get_text(resp))
        self.assertIn(url_for("room_bp.logout", _external=False), self.get_text(resp))

    def test_create_room_post(self):
        resp = self.client.post(url_for("room_bp.create_room"), data=self.rooms_info["out"])
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.lounge", room=Room.query.all()[-1],
            ), resp.location)

