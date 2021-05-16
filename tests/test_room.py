import re, os, shutil, time, random, requests

from flask import request, session, url_for

import unittest

import config as cfg
from config import config
from main import create_app, db
from views.socket.main import socketio
from models.main import db, User, Room, Settings, Log
from forms.main import CreateRoomForm, JoinRoomForm

from utils.helper import generate_id

from .main import BaseTests, rooms_info, first_time_info



class LoggedOutUserTests(BaseTests):
    def setUp(self):
        super(LoggedOutUserTests, self).setUp()

        self.rooms_info = rooms_info.copy()
        self.room = CreateRoomForm(**self.rooms_info["in"]).save(
            commit=True,
            user=self.user)

    def tearDown(self):
        del self.rooms_info
        del self.room

        super(LoggedOutUserTests, self).tearDown()

    def test_room(self):
        resp = self.unlogged_client.get(url_for("room_bp.room", room=self.room))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(url_for("room_bp.login"), resp.location)

    def test_bad_url_build(self):
        with self.assertRaises(Exception):
            url_for("room_bp.room", room=self.room.id)
        with self.assertRaises(Exception):
            url_for("room_bp.room", room=self.user)


class LoggedInUserTests(BaseTests):
    def setUp(self):
        super(LoggedInUserTests, self).setUp()

        self.rooms_info = rooms_info.copy()
        self.room = CreateRoomForm(**self.rooms_info["in"]).save(
            commit=True,
            user=self.user)

        self.another_room = CreateRoomForm(
            **self.rooms_info["another_in"]).save(
                commit=True,
                user=self.another_user)

        self.first_time_info = first_time_info.copy()

    def tearDown(self):
        del self.first_time_info
        del self.rooms_info
        del self.room

        super(LoggedInUserTests, self).tearDown()

    def test_room(self):
        resp = self.client.post(url_for("room_bp.lounge", room=self.room),
            data=self.first_time_info[1])
        self.assertEqual(resp.status_code, 302)

        resp = self.client.get(url_for("room_bp.room", room=self.room))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("Send", self.get_text(resp))
        self.assertIn(url_for("room_bp.dashboard", _external=False),
            self.get_text(resp))

    def test_room_not_joined(self):
        resp = self.another_client.get(url_for("room_bp.room", room=self.room),
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("not yet joined this room", self.get_text(resp))
        self.assertIn("Dashboard", self.get_text(resp))

    def test_room_not_entered(self):
        resp = self.client.get(url_for("room_bp.room", room=self.room),
            follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn("need to have confirmed your details", self.get_text(resp))
        self.assertIn("Lounge", self.get_text(resp))

