from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, PasswordField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Length, EqualTo, Email
from flask_wtf.file import FileField, FileRequired, FileAllowed


class UserCreateForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=1, max=25)])
    nickname = StringField('사용자별명', validators=[DataRequired(), Length(min=1, max=25)])
    password1 = PasswordField('비밀번호', validators=[DataRequired(), EqualTo('password2', '비밀번호가 일치하지 않습니다')])
    password2 = PasswordField('비밀번호확인', validators=[DataRequired()])
    email = EmailField('이메일', [DataRequired(), Email()])


class UserLoginForm(FlaskForm):
    username = StringField('사용자이름', validators=[DataRequired(), Length(min=1, max=25)])
    password = PasswordField('비밀번호', validators=[DataRequired()])


class BlogForm(FlaskForm):
    title = StringField('제목', validators=[DataRequired('블로그 제목을 입력해주세요.')])
    content = TextAreaField('블로그', validators=[DataRequired('블로그 내용을 입력해주세요.')])
    image_file = FileField('사진')


class UserFixForm(FlaskForm):
    nickname = StringField('사용자별명', validators=[DataRequired(), Length(min=1, max=25)])
    word = StringField('자기소개', validators=[DataRequired()])
    image_file = FileField('사진')
