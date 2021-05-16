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

from . import main



class BaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app("testing")
        
        cls.client = cls.app.test_client(use_cookies=True)
        cls.another_client = cls.app.test_client(use_cookies=True)
        cls.unlogged_client = cls.app.test_client(use_cookies=True)

    @classmethod
    def tearDownClass(cls):
        try:
            os.unlink("./data-test.sqlite")
        except:
            pass

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.users_info = users_info.copy()
        self.user = RegisterForm(**self.users_info["in"]["register"]).save(commit=True)
        self.client.post(url_for("room_bp.login"), data=self.users_info["in"]["login"])

        self.another_user = RegisterForm(
            **self.users_info["another_in"]["register"]).save(commit=True)
        self.another_client.post(
            url_for("room_bp.login"), data=self.users_info["another_in"]["login"])
    
    def tearDown(self):
        del self.users_info
        del self.user
        self.client.get(url_for("room_bp.logout"))

        db.session.remove()
        db.drop_all()
        os.unlink("./data-test.sqlite")
        self.app_context.pop()

    @staticmethod
    def get_text(resp):
        return resp.get_data(as_text=True)


users_info = {
    "in": {
        "create": {
            "name": "testuser_name1",
            "def_username": "testuser_username1",
            "email": "testuser1@email.com",
            "password": "somebody_cares",
        },
        "register": {
            "name": "testuser_name1",
            "def_username": "testuser_username1",
            "email": "testuser1@email.com",
            "password": "somebody_cares",
        },
        "login": {
            "email": "testuser1@email.com",
            "password": "somebody_cares",
        }
    },
    "another_in": {
        "create": {
            "name": "another_testuser",
            "def_username": "another_testusername",
            "email": "another_testuser@email.com",
            "password": "maybe_i_care",
        },
        "register": {
            "name": "another_testuser",
            "def_username": "another_testusername",
            "email": "another_testuser@email.com",
            "password": "maybe_i_care",
        },
        "login": {
            "email": "another_testuser@email.com",
            "password": "maybe_i_care",
        }
    },
    "out": {
        "create": {
            "name": "testuser_name2",
            "def_username": "testuser_username2",
            "email": "testuser2@email.com",
            "password": "nobody_cares",
        },
        "register": {
            "name": "testuser_name2",
            "def_username": "testuser_username2",
            "email": "testuser2@email.com",
            "password": "nobody_cares",
        },
        "login": {
            "email": "testuser2@email.com",
            "password": "nobody_cares",
        }
    }
}

rooms_info = {
    "in": {
        "topic": "The first",
    },
    "another_in": {
        "topic": "Another The first",
    },
    "out": {
        "topic": "The second",
    }
}

first_time_info = {
    1: {
        "username": "first-timer",
        # "email": "first-timer@email.com",
    }
}

