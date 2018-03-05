# -*- coding:utf-8 -*-
import logging
import hashlib
from datetime import datetime

import mistune
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import html

from . import db
from . import login_manager


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
    password = db.Column(db.String(256))
    email = db.Column(db.String(256))
    website = db.Column(db.String(256))

    def __init__(self, form):
        super(User, self).__init__()
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.email = form.get('email', '')
        self.website = form.get('website', '')

    def password_to_hash(self):
        self.password = generate_password_hash(self.password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        self.password_to_hash()
        db.session.add(self)
        db.session.commit()


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
    view_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    createtime = db.Column(db.DateTime, index=True, default=datetime.utcnow())
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

    def save(self, tags):
        for tag in tags:
            t = Tag.query.filter_by(name=tag).first()
            if t is None:
                t = Tag(tag)
                t.save()
            self.tags.append(t)
        db.session.add(self)
        db.session.commit()

    def delete(self):
        for c in self.comments:
            db.session.delete(c)
        db.session.delete(self)
        db.session.commit()

    def update(self, form):
        self.title = form.get('title')
        self.summary = form.get('summary')
        self.content = form.get('content')
        tags = Tag.str_to_list(form.get('tags'))
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
        self.view_count += 1
        db.session.add(self)
        db.session.commit()

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
    createtime = db.Column(db.DateTime, index=True, default=datetime.utcnow())
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

    def __init__(self, form):
        self.name = form.get('name', '')
        self.email = form.get('email', '')
        self.website = form.get('website', '')
        self.content = form.get('content', '')

    def save(self, blog):
        self.blog_id = blog.id
        self.gravatar_id = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        blog.comments_count += 1
        db.session.add(self)
        db.session.add(blog)
        db.session.commit()

    def delete(self, blog):
        blog.comments_count -= 1
        db.session.delete(self)
        db.session.add(blog)
        db.session.commit()

    def block(self):
        if not self.is_block:
            self.is_block = True
            self.blog.comments_count -= 1
            db.session.add(self)
            db.session.commit()

    def unblock(self):
        if self.is_block:
            self.is_block = False
            self.blog.comments_count += 1
            db.session.add(self)
            db.session.commit()

    @staticmethod
    def generate_fake(count=500):
        import forgery_py
        from random import seed, randint

        seed()
        blog_count = Blog.query.count()
        if blog_count > 0:
            for i in range(count):
                d = dict(
                    name=forgery_py.name.full_name(),
                    email=forgery_py.email.address(),
                    website='http://'+forgery_py.internet.domain_name(),
                    content=forgery_py.lorem_ipsum.paragraph()
                )
                c = Comment(d)
                blogs = Blog.query.all()
                c.save(blogs[randint(0, blog_count-1)])



