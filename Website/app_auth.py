
from flask import Blueprint, render_template, flash, redirect, url_for, request, Response, jsonify
from .app_models import User, Post, Like, Comment, Following, Follower, db, SearchForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, exc
from . import DB_NAME
import imghdr
import base64


# engine = create_engine(f"sqlite:///./{DB_NAME}")
app_auth = Blueprint('app_auth', __name__)


@app_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')

        # print(user_name)

        user = User.query.filter_by(user_name=user_name).first()
        # print(user)

        if user:
            # if check_password_hash(user.password, password):
            if password == user.password:
                flash('Logged in', category='success')
                login_user(user, remember=True)

                return redirect(url_for('app_views.app_feed'))
            else:
                flash("Incorrect Password", category='error')
        else:
            flash('user-name not found', category='error')

    # data = request.form
    # print(data)
    return render_template("login.html", user=current_user)


@app_auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        # print(user_name, name)
        user = User.query.filter_by(user_name=user_name).first()
        print(user)

        if user:
            flash("This user already exists. Log in", category='error')
            redirect(url_for('app_auth.login'))

        elif password != confirm_password:
            flash("Passwords don't match", category='error')
            # print("not matched")
        elif len(password) < 3:
            flash("Password is too short, should be greater than 7 characters", category='error')

        else:
            # new_user = User(user_name=user_name, name=name, password=generate_password_hash(password, method='sha256'))
            new_user = User(user_name=user_name, name=name, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Account Created!', category='success')
            login_user(new_user, remember=True)

            return redirect(url_for('app_auth.profile', user=current_user, user_name=new_user.user_name))

    return render_template('sign_up.html', user=current_user)


# @app_auth.route('/profile', methods=['GET'])
# @login_required
# def profile():
#     return render_template('profile_page.html')

@app_auth.route('/followers/<user_name>', methods=['GET', 'POST'])
@login_required
def follower(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    return render_template('followers_page.html', user=user)


@app_auth.route('/following/<user_name>', methods=['GET', 'POST'])
@login_required
def following(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    return render_template('following_page.html', user=user)


@app_auth.route('/profile/<user_name>', methods=['GET', 'POST'])
@login_required
def profile(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    flwr_count = Follower.query.filter_by(user_id=user.id).count()
    flwg_count = Following.query.filter_by(user_id=user.id).count()
    if user:
        return render_template('profile_page.html', form=SearchForm, user_name=user_name, name=user.name,
                               flwr_count=flwr_count, flwg_count=flwg_count, user=current_user)
    else:
        return "This user does not exist"


@app_auth.route('/log-out')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app_auth.login'))


@app_auth.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return redirect(url_for('app_views.app_feed'))
    searched = request.form.get('searched')
    return redirect(url_for('app_auth.searched', searched=searched))


@app_auth.route('/search/results/<searched>', methods=['POST', 'GET'])
@login_required
def searched(searched):
    lis = User.query.filter(User.id != current_user.id, User.user_name.like('%' + searched + '%')).order_by(
        User.user_name.asc())
    found = []

    for a in lis:
        temp = Following.query.filter_by(following_id=a.id, user_id=current_user.id).first()
        # temp = current_user.following
        if temp:
            found.append((a, 1, temp))
        else:
            found.append((a, 0, 0))
    # temp = current_user.following

    return render_template('searched_user.html', lis=found, user=current_user, searched=searched)


@app_auth.route('/<user_name>/create-post', methods=['GET', 'POST'])
@login_required
def create_post(user_name):
    # get the file type of the uploaded file
    if request.method == 'POST':
        file = request.files['image']
        file_type = imghdr.what(file)

        title = request.form.get('title')
        caption = request.form.get('caption')
        user_id = current_user.id

        if file_type in ['jpeg', 'png', 'gif']:
            mimetype = file.mimetype
            new_post = Post(img=file.read(), mimetype=mimetype, title=title, caption=caption, user_id=user_id)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for("app_views.app_feed"))

        else:
            return "file type not supported, Upload a Image."

    return render_template('create_post.html', user_name=user_name, user=current_user)


@app_auth.route('/post/<int:id>')
@login_required
def see_post(id):
    post_obj = Post.query.filter_by(id=id).first()
    if not post_obj:
        return "<h2>Post not found</h2>", 404

    # error code 404 = bad request

    if post_obj.hide == 1 and current_user.id != post_obj.user_id:
        return "<h2>This post is hidden and only visible to the owner.</h2>", 400
    image_data = base64.b64encode(post_obj.img).decode('utf-8')
    post_owner = User.query.filter_by(id=post_obj.user_id).first()

    likes = post_obj.likes
    # print(likes)
    comments = post_obj.comments
    likes_count = len(likes)
    comments_count = len(comments)

    liked = Like.query.filter_by(post_id=post_obj.id, liker_id=current_user.id).first()
    # print(liked)
    lkd = 0
    if liked:
        lkd = 1
    return render_template('just_a_post.html',
                           user=current_user,
                           owner=post_owner,
                           lc=likes_count,
                           cc=comments_count,
                           img_data=image_data,
                           post=post_obj,
                           lkd=lkd
                           )




