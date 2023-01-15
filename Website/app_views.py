
from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .app_models import User, Post, Like, Comment, Following, Follower, db, SearchForm
import base64

app_views = Blueprint('app_views', __name__)


@app_views.route('/', methods=['GET', 'POST'])
@login_required
def app_feed():
    posts = []
    post_objects = Post.query.filter_by(hide=0).order_by(Post.timestamp.desc())

    flwing_id = []
    for i in current_user.followings:
        flwing_id.append(i.following_id)

    for obj in post_objects:
        if obj.user_id in flwing_id or obj.user_id == current_user.id:
            posts.append(obj)

    return render_template('feed.html', user=current_user, base64=base64, User=User, Like=Like, posts=posts)


@app_views.route('/followers/<user_name>', methods=['GET', 'POST'])
@login_required
def follower(user_name):
    user_obj = User.query.filter_by(user_name=user_name).first()

    return render_template('followers_page.html', user_obj=user_obj)


@app_views.route('/following/<user_name>', methods=['GET', 'POST'])
@login_required
def following(user_name):
    user_obj = User.query.filter_by(user_name=user_name).first()
    return render_template('following_page.html', user_obj=user_obj)


@app_views.route('/profile/<user_name>', methods=['GET', 'POST'])
@login_required
def profile(user_name):
    user_obj = User.query.filter_by(user_name=user_name).first()

    if user_obj:
        return render_template('profile.html', base64=base64, user_obj=user_obj, user=current_user)
    else:
        return "This user does not exist"


@app_views.route('/post/<int:id>')
@login_required
def see_post(id):
    post_obj = Post.query.filter_by(id=id).first()

    if not post_obj or (post_obj.hide == 1 and current_user.id != post_obj.user_id):
        flash("This post is hidden and only visible to the owner.", category='error')
        return redirect(url_for('app_views.app_feed'))

    return render_template('just_a_post.html',
                           user=current_user,
                           post_obj=post_obj,
                           User=User,
                           base64=base64,
                           Like=Like
                           )


@app_views.context_processor
def base():
    form = SearchForm()
    return dict(form=form)
