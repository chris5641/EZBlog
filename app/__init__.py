# -*- coding:utf-8 -*-
import pymysql

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from config import Config

db = SQLAlchemy()
pymysql.install_as_MySQLdb()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login_view'


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    Config.init_app(app)
    db.init_app(app)
    db.app = app
    login_manager.init_app(app)

    from .main import main as main_blueprint
    from .admin import admin as admid_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(admid_blueprint, url_prefix='/admin')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
