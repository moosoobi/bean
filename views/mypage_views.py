from flask import Blueprint,render_template,url_for,request, session, g, Flask
from werkzeug.utils import redirect, secure_filename
import os

from .. import db
from ..forms import UserFixForm
from ..models import User

bp=Blueprint('mypage', __name__, url_prefix='/mypage')


@bp.route('/list/')
def _list():
    if g.user:
        level = get_level(g.user)
        level_image = '꽃' + str(level) + '.png'
    else:
        level = 1
        level_image = 'rainbow.png'

    return render_template('mypage/mypage_list.html', level_image=level_image, user_level=level)


@bp.route('/fix/', methods=('POST','GET'))
def fix():
    form = UserFixForm()

    if request.method == 'POST' and form.validate_on_submit():
        user = User.query.get(g.user.id)

        image_file = form.image_file.data

        if image_file and image_file.filename != '':
            image_file.save(os.path.join('./static', image_file.filename))
            user.image = image_file.filename

        user.nickname = form.nickname.data
        user.word = form.word.data
        db.session.commit()

        return redirect(url_for('mypage._list'))
    return render_template('mypage/profile.html', form=form)


def get_level(user):
    level = 1
    if user:
        if user.exp <= 10:
            level = 1
        elif (user.exp > 10) and (user.exp <= 20):
            level = 2
        elif (user.exp > 20) and (user.exp <= 30):
            level = 3
        elif user.exp > 30:
            level = 4
        else:
            level = 1

    return level
