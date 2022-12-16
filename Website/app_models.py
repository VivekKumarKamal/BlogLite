from . import db
from flask_login import UserMixin
from sqlalchemy import func, ForeignKey
from os import path


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    user_name = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))

    followers = db.relationship('Follower')
    followings = db.relationship('Following')


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    caption = db.Column(db.String(200))
    img_url = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# In python the convention is to name the class in capital letter
# But in line 10 "user.id"(the green one) is in sql where it is same as U

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    liker = db.Column(db.Integer)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    time = db.Column(db.DateTime(timezone=True), default=func.now())
    commenter = db.Column(db.Integer)
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


if __name__ == '__main__':
    print("created")
    init_db()
