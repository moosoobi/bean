from flask import Blueprint, url_for, flash, g
from werkzeug.utils import redirect

from bean import db
from bean.models import Blog
from bean.views.auth_views import login_required

bp = Blueprint('vote', __name__, url_prefix='/vote')


@bp.route('/blog/<int:blog_id>/')
@login_required
def blog(blog_id):
    _blog = Blog.query.get_or_404(blog_id)
    if g.user == _blog.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        _blog.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('blog.detail', blog_id=blog_id))
