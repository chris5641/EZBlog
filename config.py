# -*- coding:utf-8 -*-
import os
import logging
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY') or 'it is easy'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'mysql://root:root@{}/web'.format('db')

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s - %(asctime)s - %(filename)s[line:%(lineno)d] - %(message)s',
                        datefmt='%Y %b %d %H:%M:%S')
    BLOGS_PER_PAGE = os.getenv('BLOGS_PER_PAGE') or 8
    REDIS_URL = os.getenv('REDIS_URL') or \
        'redis://{}:6379/1'.format('red')

    # REMEMBER_COOKIE_DURATION = datetime.timedelta(hours=2)
    SYNC_PERIOD = 24 * 60 * 60

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True


class ProductConfig(Config):
    DEBUG = False

    @staticmethod
    def init_app(app):
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
        logging.info('Production OK')


config = dict(
    dev=DevConfig,
    product=ProductConfig,
    default=DevConfig,
)