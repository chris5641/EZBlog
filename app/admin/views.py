# -*- coding:utf-8 -*-
import logging

from flask import (
    render_template, request, redirect, url_for, abort, flash
)
from flask_login import login_required

from ..models import User, Blog, Tag, Comment
from . import admin
from .. import db


@admin.route('/')
@login_required
def index():
    return render_template('admin/index.html')


@admin.route('/blog-post')
@login_required
def blog_post_view():
    return render_template('admin/blog_post.html')


@admin.route('/blog/post', methods=['POST'])
@login_required
def blog_post(blogtype='blogs'):
    r = request.form
    blog = Blog(r)
    tags = Tag.str_to_list(r.get('tags'))
    blog.save(tags, blogtype)
    logging.info('post blog: {}'.format(blog))
    return redirect(url_for('main.blog_view', blog_id=blog.id))


@admin.route('/blog/delete/<blog_id>')
@login_required
def blog_delete(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    logging.info('delete blog: {}'.format(blog))
    blog.delete()
    return redirect(request.referrer)


@admin.route('/blog/edit/<blog_id>', methods=['POST'])
@login_required
def blog_edit(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    r = request.form
    blog.update(r)
    logging.info('edit blog: {}'.format(blog))
    return redirect(url_for('main.blog_view', blog_id=blog.id))


@admin.route('/blogs/')
@login_required
def blogs_manage():
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.order_by(
        Blog.createtime.desc()).paginate(page, per_page=10, error_out=False)
    blogs = pagination.items
    return render_template('admin/blogs_manage.html', blogs=blogs, pagination=pagination)


@admin.route('/comments/')
@login_required
def comments_manage():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.createtime.desc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/comments_manage.html', comments=comments, pagination=pagination)


@admin.route('/account/')
@login_required
def account_manage():
    return render_template('admin/account_manage.html')


@admin.route('/comment/delete/<comment_id>')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    logging.info('delete comment: {}'.format(comment))
    for r in comment.replys:
        r.delete()
    comment.delete()
    return redirect(request.referrer)


@admin.route('/comment/block/<comment_id>')
@login_required
def comment_block(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if comment.is_block:
        logging.info('unblock comment: {}'.format(comment))
    else:
        logging.info('block comment: {}'.format(comment))
    comment.block()
    return redirect(request.referrer)


@admin.route('/user/<user_id>', methods=['POST'])
@login_required
def info_update(user_id):
    u = User.query.get_or_404(user_id)
    user = User(request.form)
    if u.verify_password(user.password):
        u.update(user)
        logging.info('user info update: {}'.format(u))
        flash('ok')
        return redirect(url_for('admin.account_manage'))
    flash('fail')
    return redirect(url_for('admin.account_manage'))


@admin.route('/password/<user_id>', methods=['POST'])
@login_required
def edit_password(user_id):
    u = User.query.get_or_404(user_id)
    ex_password = request.form.get('ex-password', '')
    new_password = request.form.get('new-password', '')
    re_password = request.form.get('re-password', '')
    if u.verify_password(ex_password) and new_password == re_password:
        u.edit_password(new_password)
        logging.info('user edit password: {}'.format(u))
        flash('ok')
        return redirect(url_for('admin.account_manage'))
    flash('fail')
    return redirect(url_for('admin.account_manage'))

