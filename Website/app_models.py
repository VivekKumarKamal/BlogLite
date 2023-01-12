from . import db
from flask_login import UserMixin
from sqlalchemy import func, ForeignKey
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea
from wtforms import StringField, SubmitField, PasswordField

from os import path







class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    user_name = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20))
    profile_pic = db.Column(db.LargeBinary)
    mimetype = db.Column(db.Text)
    about = db.Column(db.String(200))

    followers = db.relationship('Follower')
    followings = db.relationship('Following')

    posts = db.relationship('Post', backref='user', passive_deletes=True)

    likes = db.relationship('Like', backref='user', passive_deletes=True)
    comments = db.relationship('Comment', backref='user', passive_deletes=True)

# backref: it references back means from likes we can access the user who liked,
# if not put only can access likes form the user

# passive_deletes: delete all the likes/comments when user is deleted,,,,,,works with the cascade thing below

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20), nullable=False)
    caption = db.Column(db.String(200))
    img = db.Column(db.Text)
    mimetype = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    hide = db.Column(db.Integer, default=0)

    likes = db.relationship('Like', backref='post', passive_deletes=True)
    comments = db.relationship('Comment', backref='post', passive_deletes=True)


# In python the convention is to name the class in capital letter
# But in line 10 "user.id"(the green one) is in sql where it is same as U

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    liker_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

# ondelete cascade: Delete it when parent is deleted

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete="CASCADE"), nullable=False)
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    commenter = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    comment = db.Column(db.String(150), nullable=False)


class Following(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    following_id = db.Column(db.Integer)


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    follower_id = db.Column(db.Integer)


def init_db():
    db.create_all()

class SearchForm(FlaskForm):
    searched_user = StringField('Searched', validators=[DataRequired()])
    submit = SubmitField('Submit')


if __name__ == '__main__':
    print("created")
    init_db()
