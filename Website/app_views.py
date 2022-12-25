import json

from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .app_models import User, Post, Like, Comment, Following, Follower, db, SearchForm


app_views = Blueprint('app_views', __name__)

@app_views.route('/', methods=['GET', 'POST'])
@login_required
def app_feed():
    return render_template('feed.html', user=current_user)


@app_views.route('/remove-follower', methods=['POST'])
def remove_follower():
    flwr = json.loads(request.data)
    flwr_id = flwr['flwrId']
    flwr = Follower.query.get(flwr_id)
    print("what the fuck")
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
    try:
        person = json.loads(request.data)
        person_id = person['personId']

        new_following = Following(user_id=current_user.id, following_id=person_id)
        db.session.add(new_following)
        db.session.commit()

        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)})

@app_views.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

@app_views.route('/like-post/<post_id>', methods=['GET'])
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    liked = Like.query.filter_by(liker_id=current_user.id, post_id=post_id).first()

    if not post:
        flash("Post not found", category='error')
    elif liked:
        db.session.delete(liked)
        db.session.commit()
    else:
        liked = Like(liker_id=current_user.id, post_id=post_id)
        db.session.add(liked)
        db.session.commit()

    return redirect(url_for('app_auth.see_post', id=post_id))
