import json

from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
from . import db
from .app_models import User, Post, Like, Comment, Following, Follower, db


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
    if flwr:
        print(flwr)
        if flwr.user_id == current_user.id:
            db.session.delete(flwr)
            db.session.commit()
    return jsonify({})
