# -*- coding:utf-8 -*-
import logging

from flask import (
    render_template, request, redirect, url_for, abort
)
from flask_login import login_required

from ..models import Blog, Tag, Comment, Reply
from . import admin


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
def blog_post():
    r = request.form
    blog = Blog(r)
    tags = Tag.str_to_list(r.get('tags'))
    blog.save(tags)
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
    pagination = Blog.query.order_by(Blog.createtime.desc()).paginate(page, per_page=10, error_out=False)
    blogs = pagination.items
    return render_template('admin/blogs_manage.html', blogs=blogs, pagination=pagination)


@admin.route('/comments/')
@login_required
def comments_manage():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.createtime.desc()).paginate(page, per_page=10, error_out=False)
    comments = pagination.items
    return render_template('admin/comments_manage.html', comments=comments, pagination=pagination)


@admin.route('/comment/delete/<comment_id>')
@login_required
def comment_delete(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    blog_id = comment.blog_id
    blog = Blog.query.get_or_404(blog_id)
    logging.info('delete comment: {}'.format(comment))
    for r in comment.replys:
        r.delete(comment)
    comment.delete(blog)
    return redirect(request.referrer)


@admin.route('/comment/block/<comment_id>')
@login_required
def comment_block(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    logging.info('block comment: {}'.format(comment))
    for r in comment.replys:
        r.block()
    comment.block()
    return redirect(request.referrer)


@admin.route('/reply/delete/<reply_id>')
@login_required
def reply_delete(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    comment_id = reply.comment_id
    comment = Comment.query.get_or_404(comment_id)
    logging.info('delete reply: {}'.format(reply))
    reply.delete(comment)
    return redirect(request.referrer)


@admin.route('/reply/block/<reply_id>')
@login_required
def reply_block(reply_id):
    reply = Reply.query.get_or_404(reply_id)
    logging.info('block reply: {}'.format(reply))
    reply.block()
    return redirect(request.referrer)

