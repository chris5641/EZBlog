# -*- coding:utf-8 -*-
import logging

from flask import (
    request, jsonify
)
from flask_login import login_required

from . import api
from ..models import Comment, Blog


@api.route('/blogs/<blog_id>', methods=['DELETE'])
@login_required
def blog_delete(blog_id):
    r = {}
    blog = Blog.query.get_or_404(blog_id)
    logging.info('delete blog: {}'.format(blog))
    blog.delete()
    r['status'] = True
    return jsonify(r)
