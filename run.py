# -*- coding:utf-8 -*-
import os

from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment

from app import create_app, db
from app.models import User, Blog, Comment, Tag, Scheduler, sync_to_sql

app = create_app(os.getenv('config') or 'default')

manager = Manager(app)
migrate = Migrate(app, db)
moment = Moment(app)

scheduler = Scheduler(app.config['SYNC_PERIOD'], sync_to_sql)


def make_shell_context():
    return dict(app=app, db=db, User=User, Blog=Blog, Comment=Comment, Tag=Tag)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

app.jinja_env.globals['Comment'] = Comment
app.jinja_env.globals['Blog'] = Blog
app.jinja_env.globals['User'] = User
app.jinja_env.globals['Tag'] = Tag
app.jinja_env.globals['red'] = app.red


@manager.command
def build_db():
    db.drop_all()
    db.create_all()
    User.insert_user()
    Blog.insert_blog()
    app.red.flushall()
    print('build database OK')


@manager.command
def test_data():
    print('start generate fake data')
    Blog.generate_fake()
    Comment.generate_fake()
    Comment.generate_fake(reply=True)
    print('generate fake data ok!')


if __name__ == '__main__':
    # build_db()
    # test_data()
    scheduler.start()
    manager.run()

