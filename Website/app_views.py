from flask import Blueprint, render_template, flash, request, jsonify
from flask_login import login_required, current_user
from . import db
from .app_models import User, Post, Like, Comment, Following, Followers, db


app_views = Blueprint('app_views', __name__)

@app_views.route('/', methods=['GET', 'POST'])
@login_required
def app_feed():

    return render_template('feed.html')

