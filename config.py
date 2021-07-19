import re, os

import uuid
from werkzeug import security
from werkzeug.utils import secure_filename



class Config(object):
    APPLICATION_DIR = os.path.dirname(os.path.realpath(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32)
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SALT_LENGTH = 13
    STATIC_DIR = os.path.join(APPLICATION_DIR, 'static/')
    UPLOAD_DIRS = {
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SALT_LENGTH = 4
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///%s/data-dev.sqlite' % Config.APPLICATION_DIR


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SALT_LENGTH = 4
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///%s/data-test.sqlite' % Config.APPLICATION_DIR
    WTF_CSRF_ENABLED = False
    SERVER_NAME = "tests.app:5000"


class ProductionConfig(Config):
    DEBUG = False
    SALT_LENGTH = 13
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///%s/data-prod.sqlite' % Config.APPLICATION_DIR

    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1)


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig}


# Used by routes/urls for indicating the formtype.
FORMTYPE_CREATE = "build"
FORMTYPE_JOIN = "join"


# Constants related to Room model
class RoomConstant:
    NUM_LOWER_LIMIT = 100 # inclusive
    NUM_UPPER_LIMIT = 999999 # inclusive

    KIND_OPEN = 10 # anyone can join
    KIND_CLOSE = 20 # anyone can join but by invite only
    KIND_PRIVATE = 30 # anyone in an enterprise can join
    KIND_EXCLUSIVE = 40 # anyone in an enterprise can join but by invite only


# Constants related to Log model
class LogConstant:
    CAT_ROOM = 10 # to everyone in the room - notification
    CAT_ADMIN = 20 # to the room admin only
    CAT_CHAT = 30 # to everyone in the room - chat
    CAT_USER = 40 # to a particular user

