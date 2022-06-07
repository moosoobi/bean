from datetime import datetime
from datetime import timedelta

from flask import Blueprint, render_template, request, url_for, g, flash
from sqlalchemy import func
from werkzeug.utils import redirect

from .. import db
from ..forms import BlogForm
from ..models import Blog, User, Subject, blog_voter
from ..views.auth_views import login_required
import os

bp = Blueprint('blog', __name__, url_prefix='/blog')


@bp.route('/list/')
def _list():
    # 입력 파라미터
    subject_name = get_subject()

    # 최신 순으로 blog list를 가져온다.
    blog_list = Blog.query.filter(Blog.subject_name==subject_name).order_by(Blog.create_date.desc())

    # 페이지없이 모든 item을 가져온다.
    blog_list = blog_list.paginate()

    # 현재 User의 블로그 개수를 가져온다.
    if g.user:
        blog_user_count = g.user.exp
    else:
        blog_user_count = 0
    return render_template('blog/blog_list.html', subject_name=subject_name, blog_list=blog_list, blog_user_count=blog_user_count)


@bp.route('/all/')
def _all():
    # 입력 파라미터
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    so = request.args.get('so', type=str, default='recent')
    subject_name = get_subject()

    # 정렬
    if so == 'recommend':
        sub_query = db.session.query(blog_voter.c.blog_id, func.count('*').label('num_voter')) \
            .group_by(blog_voter.c.blog_id).subquery()
        blog_list = Blog.query \
            .outerjoin(sub_query, Blog.id == sub_query.c.blog_id) \
            .order_by(sub_query.c.num_voter.desc(), Blog.create_date.desc())
    else:  # recent
        blog_list = Blog.query.order_by(Blog.create_date.desc())

    # 조회
    if kw:
        search = '%%{}%%'.format(kw)
        blog_list = blog_list \
            .join(User) \
            .filter(Blog.title.ilike(search) |  # 질문제목
                    Blog.content.ilike(search) |  # 질문내용
                    User.username.ilike(search)   # 질문작성자
                    ) \
            .distinct()

    # 페이징
    blog_list = blog_list.paginate(page, per_page=10)
    return render_template('blog/blog_all.html', subject_name=subject_name, blog_list=blog_list, page=page, kw=kw, so=so)


@bp.route('/detail/<int:blog_id>/')
def detail(blog_id):
    form = BlogForm()
    blog = Blog.query.get_or_404(blog_id)
    return render_template('blog/blog_detail.html', blog=blog, form=form)


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    form = BlogForm()
    subject_name = get_subject()
    if request.method == 'POST' and form.validate_on_submit():
        blog = Blog(subject_name=subject_name, user=g.user, title=form.title.data, content=form.content.data,
                    create_date=datetime.now())
        db.session.add(blog)
        db.session.commit()
        blog.user.exp = blog.user.exp + 1
        db.session.commit()
        image_file = form.image_file.data
        if image_file and image_file.filename != '':
            arr = image_file.filename.split('.')
            filename = "{}.{}".format(blog.id, arr[len(arr)-1].lower())
            image_file.save("bean/static/images/{}".format(filename))
            blog.image_name = filename
            db.session.commit()
        return redirect(url_for('blog._list'))
    return render_template('blog/blog_form.html', subject_name=subject_name, form=form)


@bp.route('/modify/<int:blog_id>', methods=('GET', 'POST'))
@login_required
def modify(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if g.user != blog.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('blog.detail', blog_id=blog_id))
    if request.method == 'POST':
        form = BlogForm()
        if form.validate_on_submit():
            form.populate_obj(blog)
            blog.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('blog.detail', blog_id=blog_id))
    else:
        form = BlogForm(obj=blog)
    return render_template('blog/blog_modify_form.html', form=form, blog=blog)


@bp.route('/delete/<int:blog_id>')
@login_required
def delete(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    if g.user != blog.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('blog.detail', blog_id=blog_id))
    if blog:
        # image file 삭제
        if blog.image_name:
            filename = './bean/static/images/' + blog.image_name
            if os.path.exists(filename):
                os.remove(filename)
        db.session.delete(blog)
        db.session.commit()
    return redirect(url_for('blog._list'))


@bp.route('/subject/')
def get_subject():
    current_time = datetime.now()
    # 현재 시간이 9시 보다 작으면 기준 시작 일을 전날로 하고 아니면 오늘로 한다.
    if current_time.hour < 9:
        begin_time = current_time + timedelta(days=-1)
    else:
        begin_time = current_time
    # 현재 시간이 9시 보다 크거나 같으면 기준 종료 일을 다음 날로 하고 아니면 오늘로 한다.
    if current_time.hour >= 9:
        end_time = current_time + timedelta(days=1)
    else:
        end_time = current_time
    # 기준 시작 datetime과 종료 datetime을 설정한다.
    begin_time = datetime(begin_time.year, begin_time.month, begin_time.day, 9, 0, 0)
    end_time = datetime(end_time.year, end_time.month, end_time.day, 9, 0, 0)
    # db의 Subject table에서 가장 최근에 설정된 subject를 가져온다.
    subject = Subject.query.order_by(Subject.subject_now.desc()).first()
    # 가장 최근에 설정된 subject가 기준 시작과 종료 datetime 사이에 있으면 가져온 subject_name 으로 주제를 정하고
    # 아니면 새로운 주제를 random 으로 설정한다.
    if (subject.subject_now >= begin_time) and (subject.subject_now < end_time):
        subject_name = subject.subject_name
    else:
        subject_name = get_new_subject(subject.id)
    return subject_name


def get_new_subject(current_subject_id):
    import random
    subject_count = Subject.query.count()
    subject_id = current_subject_id
    loop_max = subject_count
    loop_count = 1
    while loop_count <= loop_max and subject_id == current_subject_id:
        subject_id = random.randrange(1, subject_count+1)
        loop_count = loop_count + 1
    subject = Subject.query.get(subject_id)
    subject.subject_now = datetime.now()
    db.session.commit()
    return subject.subject_name
