from bean import db


blog_voter = db.Table(
    'blog_voter',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('blog_id', db.Integer, db.ForeignKey('blog.id', ondelete='CASCADE'), primary_key=True)
)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    nickname = db.Column(db.String(150), unique=True, nullable=False)
    exp = db.Column(db.Integer, nullable=True)
    word = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(100),  nullable=True)


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(20), nullable=False)
    subject_now = db.Column(db.DateTime(), nullable=False)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(20), db.ForeignKey('subject.subject_name', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('blog_set'))
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text(), nullable=False)
    image_name = db.Column(db.String, nullable=True)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime(), nullable=True)
    voter = db.relationship('User', secondary=blog_voter, backref=db.backref('blog_voter_set'))


