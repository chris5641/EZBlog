# -*- coding:utf-8 -*-
import logging

from flask import request, jsonify
from flask_login import login_required

from . import api
from ..models import Comment, Blog


@api.route('/comments/', methods=['POST'])
def comment_add():
    form = request.form
    reply = None
    reply_id = int(form.get('reply_id', ''))
    blog_id = int(form.get('blog_id', ''))
    blog = Blog.query.get_or_404(blog_id)
    if reply_id > 0:
        reply = Comment.query.get_or_404(reply_id)
    comment = Comment(form)
    comment.save(blog, reply)
    logging.info('add comment: {}'.format(comment))
    data = comment.to_json()
    return jsonify(data)


@api.route('/comments/<comment_id>', methods=['DELETE'])
@login_required
def comment_delete(comment_id):
    r = {}
    comment = Comment.query.get_or_404(comment_id)
    logging.info('delete comment: {}'.format(comment))
    for reply in comment.replys:
        reply.delete()
    comment.delete()
    r['status'] = True
    return jsonify(r)
