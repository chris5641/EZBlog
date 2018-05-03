# -*- coding:utf-8 -*-
import pymysql
import redis
import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_apscheduler import APScheduler

from config import config

db = SQLAlchemy()
pymysql.install_as_MySQLdb()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'main.login_view'

scheduler = APScheduler()


def create_app(config_name):
    app = Flask(__name__)

    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    db.app = app
    login_manager.init_app(app)
    app.permanent_session_lifetime = datetime.timedelta(hours=3)
    app.red = redis.Redis().from_url(config[config_name].REDIS_URL)

    from .main import main as main_blueprint
    from .admin import admin as admid_blueprint
    from .api import api as api_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(admid_blueprint, url_prefix='/admin')
    app.register_blueprint(api_blueprint, url_prefix='/api')

    scheduler.init_app(app)

    return app
