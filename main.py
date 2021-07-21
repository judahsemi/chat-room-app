
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

import config as cfg
from config import config



login_manager = LoginManager()
login_manager.login_view = "user_bp.login"
db = SQLAlchemy()
socketio = SocketIO()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    login_manager.init_app(app)
    db.init_app(app)
    socketio.init_app(app)

    # Converters
    from utils import converter
    
    app.url_map.converters["real_room"] = converter.RealRoom

    # Views
    from views.user.main import user_bp
    from views.room.main import room_bp
    
    app.register_blueprint(user_bp, url_prefix="")
    app.register_blueprint(room_bp, url_prefix="")

    return app

