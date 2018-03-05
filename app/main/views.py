# -*- coding:utf-8 -*-
import logging

from flask import (
    render_template, request, url_for, redirect, abort, current_app
)
from flask_login import login_user, logout_user, login_required

from ..models import Blog, User, Tag, Comment
from . import main


@main.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(Blog.createtime.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items
    # blogs = Blog.query.all()
    tags = Tag.query.order_by(Tag.id).all()
    return render_template('main/index.html', blogs=blogs, tags=tags, pagination=pagination)


@main.route('/login/')
def login_view():
    return render_template('admin/login.html')


@main.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/login', methods=['POST'])
def login():
    user = User(request.form)
    u = User.query.filter_by(username=user.username).first()
    if u is not None and u.verify_password(user.password):
        login_user(u)
        logging.info('log in: {}'.format(u))
        return redirect(url_for('main.index'))
    abort(404)


@main.route('/blogs/<blog_id>')
def blog_view(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    blog.click()
    return render_template('main/blog.html', blog=blog)


@main.route('/tags/<tag_id>')
def tag_view(tag_id):
    tag = Tag.query.get_or_404(tag_id)
    tags = Tag.query.all()
    page = request.args.get('page', 1, type=int)
    pagination = tag.blogs.order_by(Blog.createtime.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items
    return render_template('main/index.html', blogs=blogs, tags=tags, pagination=pagination)


@main.route('/about/')
def about_view():
    return render_template('main/about.html')






