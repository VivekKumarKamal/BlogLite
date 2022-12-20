import json

from flask import Blueprint, render_template, flash, request, jsonify
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
    person = json.loads(request.data)
    person_id = person['personId']
    person = Following.query.get(person_id)
    if person:
        db.session.add(person)
        db.session.commit()
    return jsonify({})

@app_views.context_processor
def base():
    form = SearchForm()
    return dict(form=form)
