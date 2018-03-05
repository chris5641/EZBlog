# -*- coding:utf-8 -*-
import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('SECRET_KEY') or 'it is easy'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'mysql://web:web@localhost/ez'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(filename)s[line:%(lineno)d] - %(message)s',
                        datefmt='%Y %b %d %H:%M:%S')
    BLOGS_PER_PAGE = os.getenv('BLOGS_PER_PAGE') or 8
    SESSION_PROTECTION = 'strong'

    @staticmethod
    def init_app(app):
        pass
