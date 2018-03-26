# -*- coding:utf-8 -*-
import logging
import hashlib
from datetime import datetime
from threading import Timer

import mistune
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

from . import db
from . import login_manager


class Scheduler(object):
    def __init__(self, sleep_time, func):
        self.sleep_time = sleep_time
        self.func = func
        self._t = None

    def start(self):
        if self._t is None:
            self._t = Timer(self.sleep_time, self._run)
            self._t.start()
        else:
            raise Exception('Timer is already running!')

    def _run(self):
        self.func()
        self._t = Timer(self.sleep_time, self._run)
        self._t.start()

    def stop(self):
        if self._t is not None:
            self._t.cancel()
            self._t = None


def sync_to_sql():
    blogs = Blog.query.all()
    logging.info('Syncing blogs!')
    for b in blogs:
        count = current_app.red.get('view_count:{}'.format(b.id))
        if count is not None:
            b.sync(int(count))
    logging.info('Syncd blogs!')


class HighlightRenderer(mistune.Renderer):
    def block_code(self, code, lang):
        if not lang:
            return'\n<pre><code>{}</code></pre>\n'.format(mistune.escape(code))
        lexer = get_lexer_by_name(lang, stripall=True)
        formatter = html.HtmlFormatter()
        return highlight(code, lexer, formatter)


renderer = HighlightRenderer()
markdown = mistune.Markdown(renderer=renderer)


association_table = db.Table('association',
                             db.Column('blog_id', db.Integer, db.ForeignKey('blogs.id')),
                             db.Column('tag_id', db.Integer, db.ForeignKey('tags.id')),
                             )


class ModelMixin(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        return '{}: {}'.format(class_name, self.id)


class User(db.Model, ModelMixin, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    nickname = db.Column(db.String(64))
    password = db.Column(db.String(256))
    email = db.Column(db.String(256))
    website = db.Column(db.String(256))
    title = db.Column(db.String(256))
    gravatar_id = db.Column(db.String(64))

    def __init__(self, form):
        super(User, self).__init__()
        self.username = form.get('username', '')
        self.nickname = form.get('nickname', '')
        self.password = form.get('password', '')
        self.email = form.get('email', '')
        self.website = form.get('website', '')
        self.title = form.get('title', '')

    def password_to_hash(self):
        self.password = generate_password_hash(self.password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        self.password_to_hash()
        self.gravatar_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

    def update(self, user):
        self.username = user.username
        self.nickname = user.nickname
        self.email = user.email
        self.website = user.website
        self.title = user.title
        self.gravatar_id = hashlib.md5(user.email.lower().encode('utf-8')).hexdigest()
        db.session.add(self)
        db.session.commit()

    def edit_password(self, password):
        self.password = generate_password_hash(password)
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def insert_user():
        d = dict(
            username='admin',
            password='admin',
            nickname='admin',
            email='',
            website='',
            title='EZBlog',
        )
        u = User(d)
        u.save()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class Blog(db.Model, ModelMixin):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    summary = db.Column(db.Text)
    summary_html = db.Column(db.Text)
    content = db.Column(db.Text)
    content_html = db.Column(db.Text)
    type = db.Column(db.String(64), default='blog')
    view_count = db.Column(db.Integer, default=0)
    createtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    comments = db.relationship('Comment', backref='blog', lazy='dynamic')
    tags = db.relationship('Tag', secondary=association_table,
                           backref=db.backref('blogs', lazy='dynamic'),
                           lazy='dynamic')

    def __init__(self, form):
        super(Blog, self).__init__()
        self.title = form.get('title', '')
        self.summary = form.get('summary', '')
        self.content = form.get('content', '')

    @staticmethod
    def content_to_html(target, value, oldvalue, initiator):
        target.content_html = markdown(value)

    @staticmethod
    def summary_to_html(target, value, oldvalue, initiator):
        target.summary_html = markdown(value)

    def save(self, tags='', blogtype='blog'):
        for tag in tags:
            t = Tag.query.filter_by(name=tag).first()
            if t is None:
                t = Tag(tag)
                t.save()
            self.tags.append(t)
        self.type = blogtype
        db.session.add(self)
        db.session.commit()

    def delete(self):
        if self.type == 'blog':
            for c in self.comments:
                db.session.delete(c)
            db.session.delete(self)
            db.session.commit()

    def update(self, form):
        self.title = form.get('title', self.title)
        self.summary = form.get('summary', self.summary)
        self.content = form.get('content', self.content)
        tags = Tag.str_to_list(form.get('tags', ''))
        for t in self.tags.all():
            if t.name not in tags:
                self.tags.remove(t)

        for tag in tags:
            t = self.tags.filter_by(name=tag).first()
            if t:
                continue
            t = Tag.query.filter_by(name=tag).first()
            if t is None:
                t = Tag(tag)
                t.save()
            self.tags.append(t)
        db.session.add(self)
        db.session.commit()

    def click(self):
        count = current_app.red.get('view_count:{}'.format(self.id))
        if count is None:
            current_app.red.set('view_count:{}'.format(self.id), self.view_count)
            count = self.view_count
        current_app.red.incr('view_count:{}'.format(self.id))
        count = int(count)
        if (count + 1) % 100 == 0:
            self.view_count = count + 1
            db.session.add(self)
            db.session.commit()
            current_app.red.delete('view_count:{}'.format(self.id))

    def get_view_count(self):
        if current_app.red.exists('view_count:{}'.format(self.id)):
            return int(current_app.red.get('view_count:{}'.format(self.id)))
        else:
            return self.view_count

    def sync(self, count):
        self.view_count = count
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def insert_blog():
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
        hello = dict(
            title='Hello Wrold',
            summary='你好世界！这篇是由EZBlog自动生成，欢迎使用！',
            content='你好世界！这篇是由EZBlog自动生成，欢迎使用！',
        )
        b = Blog(about)
        b.save(blogtype='about')
        b = Blog(project)
        b.save(blogtype='project')
        b = Blog(hello)
        b.save()

    @staticmethod
    def generate_fake(count=50):
        from random import seed, randint, sample
        import forgery_py
        tag_list = [
            'Python', 'JavaScript', '前端', '后端', '感悟', 'C', '算法', 'LeetCode', 'others', 'Docker', '爬虫'
        ]

        seed()
        for i in range(count):
            d = dict(
                title=forgery_py.lorem_ipsum.title(randint(2, 5)),
                summary=forgery_py.lorem_ipsum.paragraph(),
                content=forgery_py.lorem_ipsum.paragraphs(quantity=randint(4, 10), sentences_quantity=randint(3, 8)),
            )
            tags = sample(tag_list, randint(0, 4))
            b = Blog(d)
            b.createtime = forgery_py.date.datetime(True, 0, 1000)
            b.save(tags)


db.event.listen(Blog.content, 'set', Blog.content_to_html)
db.event.listen(Blog.summary, 'set', Blog.summary_to_html)


class Tag(db.Model, ModelMixin):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)

    def __init__(self, name):
        self.name = name

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def str_to_list(string):
        if string == '':
            return []
        return string.split(',')


class Comment(db.Model, ModelMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    email = db.Column(db.String(64))
    website = db.Column(db.String(256))
    content = db.Column(db.Text)
    gravatar_id = db.Column(db.String(64))
    is_block = db.Column(db.Boolean, default=False)
    is_child = db.Column(db.Boolean, default=False)
    createtime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    reply_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    replys = db.relationship('Comment', lazy='dynamic')
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

    def __init__(self, form):
        self.name = form.get('name', '')
        self.email = form.get('email', '')
        self.website = form.get('website', '')
        self.content = form.get('content', '')

    def save(self, blog, comment=None):
        self.blog_id = blog.id
        self.gravatar_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        if comment and comment.blog.id == blog.id:
            self.reply_id = comment.id
            self.is_child = True
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def to_json(self):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'website': self.website,
            'content': self.content,
            'create_time': self.createtime,
            'gravatar_id': self.gravatar_id,
            'is_child': self.is_child,
            'reply_id': self.reply_id,
        }
        return data

    def block(self):
        self.is_block = not self.is_block
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def generate_fake(count=500, reply=False):
        import forgery_py
        from random import seed, randint

        seed()
        blogs_count = Blog.query.count()
        comments_count = Comment.query.count()
        if blogs_count > 0:
            blogs = Blog.query.all()
            comments = Comment.query.all()
            for i in range(count):
                d = dict(
                    name=forgery_py.name.full_name(),
                    email=forgery_py.email.address(),
                    website='http://'+forgery_py.internet.domain_name(),
                    content=forgery_py.lorem_ipsum.paragraph()
                )
                c = Comment(d)
                c.createtime = forgery_py.date.datetime(True, 0, 1000)
                if reply:
                    comment = comments[randint(0, comments_count - 1)]
                    c.save(comment.blog, comment)
                else:
                    c.save(blogs[randint(0, blogs_count-1)])

