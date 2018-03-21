# -*- coding:utf-8 -*-
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment

from app import create_app, db
from app.models import User, Blog, Comment, Tag

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)
moment = Moment(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Blog=Blog, Comment=Comment, Tag=Tag)


manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

app.jinja_env.globals['Comment'] = Comment
app.jinja_env.globals['Blog'] = Blog
app.jinja_env.globals['User'] = User
app.jinja_env.globals['Tag'] = Tag


def build_db():
    print('start build database')
    db.drop_all()
    db.create_all()
    admin = dict(
        username='admin',
        password='admin',
        nickname='admin',
        email='wangchong9139@gmail.com',
        website='https://www.baidu.com',
        title='EZBlog',
    )
    about = dict(
        title='关于',
        summary='',
        content='',
    )
    project = dict(
        title='项目',
        summary='',
        content='',
    )
    u = User(admin)
    u.save()
    b = Blog(about)
    b.save(blogtype='about')
    b = Blog(project)
    b.save(blogtype='project')
    Blog.generate_fake()
    Comment.generate_fake()
    Comment.generate_fake(reply=True)

    print('build database OK')


if __name__ == '__main__':
    # build_db()
    manager.run()
