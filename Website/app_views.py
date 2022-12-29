import json

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

    for obj in post_objects:
        image_data = base64.b64encode(obj.img).decode('utf-8')
        tup = (obj, image_data)
        posts.append(tup)

    return render_template('feed.html', user=current_user, User=User, Like=Like, posts=posts)



@app_views.route('/remove-follower', methods=['POST'])
def remove_follower():
    flwr = json.loads(request.data)
    flwr_id = flwr['flwrId']
    flwr = Follower.query.get(flwr_id)
    if flwr:
        # print(flwr)
        if flwr.user_id == current_user.id:
            db.session.delete(flwr)
            db.session.commit()
    return jsonify({})

@app_views.route('/unfollow', methods=['POST'])
def unfollow():
    flwg = json.loads(request.data)
    flwg_id = flwg['flwgId']
    flwg = Following.query.get(flwg_id)
    if flwg:
        if flwg.user_id == current_user.id:
            db.session.delete(flwg)
            db.session.commit()
    return jsonify({})

@app_views.route('/follow', methods=['POST'])
def follow():
        person = json.loads(request.data)
        person_id = person['personId']

        new_following = Following(user_id=current_user.id, following_id=person_id)
        db.session.add(new_following)
        db.session.commit()

        return jsonify({})

@app_views.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app_views.route('/like-post-<post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    liked = Like.query.filter_by(liker_id=current_user.id, post_id=post_id).first()
    print(liked)
    val = False
    if not post:
        flash("Post not found", category='error')
        return jsonify({'error': 'Post not found'}, 400)
    elif liked:
        db.session.delete(liked)
        db.session.commit()
    else:
        liked = Like(liker_id=current_user.id, post_id=post_id)
        db.session.add(liked)
        db.session.commit()
        val = True
    return jsonify({"likes_count": len(post.likes), "liked": val})

@app_views.route("/hide-post-<post_id>")
@login_required
def hide_post(post_id):

    post = Post.query.filter_by(id=post_id).first()
    if current_user.id != post.user_id:
        return "Any one other than Author cannot hide the post.", 404
    if post.hide == 0:
        post.hide = 1
    else:
        post.hide = 0
    db.session.commit()
    flash('Post hidden Successfully', category='success')
    return redirect(url_for('app_views.app_feed'))

@app_views.route("/delete-post-<post_id>", methods=["POST"])
@login_required
def delete_post(post_id):

    post = Post.query.filter_by(id=post_id).first()
    if current_user.id != post.user_id:
        flash('Any one other than Author cannot delete the post.', category='error')
    else:
        for like in post.likes:
            db.session.delete(like)
            db.session.commit()
        for comment in post.comments:
            db.session.delete(comment)
            db.session.commit()

        db.session.delete(post)
        db.session.commit()
        flash('Post Deleted Successfully', category='success')
    return redirect(url_for('app_views.app_feed'))

@app_views.route("/create-comment/<int:post_id>", methods=['POST'])
@login_required
def create_comment(post_id):
    comment = request.form.get('comment')
    if not comment:
        flash("Comment cannot be empty.", category='error')
    else:
        post = Post.query.filter_by(id=post_id)
        if post:
            comment_obj = Comment(comment=comment, commenter=current_user.id, post_id=post_id)
            db.session.add(comment_obj)
            db.session.commit()
        else:
            flash("Post does not exit", category='error')
    return redirect(url_for('app_views.app_feed'))
