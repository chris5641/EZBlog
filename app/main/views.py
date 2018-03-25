# -*- coding:utf-8 -*-
import logging

from flask import (
    render_template, request, url_for, redirect, abort, current_app
)
from sqlalchemy import extract, func, desc
from flask_login import current_user

from ..models import Blog, User, Tag, Comment
from . import main
from .. import db


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.filter_by(type='blog').order_by(Blog.createtime.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items
    tags = Tag.query.order_by(Tag.id).all()
    return render_template('main/index.html', blogs=blogs, tags=tags, pagination=pagination)


@main.route('/login/')
def login_view():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))
    return render_template('admin/login.html')


@main.route('/blogs/<blog_id>')
def blog_view(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    comments = blog.comments.filter_by(is_child=False).order_by(Comment.createtime)
    blog.click()
    return render_template('main/blog.html', blog=blog, comments=comments)


@main.route('/about/')
def about_view():
    blog = Blog.query.filter_by(type='about').first_or_404()
    comments = blog.comments.filter_by(is_child=False).order_by(Comment.createtime)
    blog.click()
    return render_template('main/blog.html', blog=blog, comments=comments)


@main.route('/project/')
def project_view():
    blog = Blog.query.filter_by(type='project').first_or_404()
    comments = blog.comments.filter_by(is_child=False).order_by(Comment.createtime)
    blog.click()
    return render_template('main/blog.html', blog=blog, comments=comments)


@main.route('/archives/')
def archives_view():
    tags = Tag.query.order_by(Tag.id).all()
    blogs_group = []
    archives = db.session.query(extract('year', Blog.createtime).label('year'),
                                func.count('*').label('count')).group_by('year').order_by(desc('year')).all()
    for archive in archives:
        blogs_group.append((archive[0], db.session.query(Blog).filter(
            extract('year', Blog.createtime) == archive[0], Blog.type == 'blog').order_by(desc('createtime')).all()))
    return render_template('main/archives.html', blogs_group=blogs_group, tags=tags)


@main.route('/tags/<tag_id>')
def tag_view(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = tag.blogs.order_by(Blog.createtime.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items
    return render_template('main/index.html', blogs=blogs, tags=tags, pagination=pagination)







