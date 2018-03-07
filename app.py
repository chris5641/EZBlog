# -*- coding:utf-8 -*-
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment

from app import create_app, db
from app.models import User, Blog, Comment, Tag, Reply

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
moment = Moment(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Blog=Blog, Comment=Comment, Tag=Tag, Reply=Reply)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


def build_db():
    db.drop_all()
    db.create_all()
    admin = dict(
        username='chris',
        password='admin',
        email='wangchong9139@gmail.com',
        website='https://www.baidu.com',
    )
    u = User(admin)
    u.save()
    Blog.generate_fake()
    Comment.generate_fake()
    Reply.generate_fake()

    print('create database OK')


if __name__ == '__main__':
    # build_db()
    manager.run()
