import json

from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from .app_models import User, Post, Like, Comment, Following, Follower, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import func
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
        # print(user)

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

            return redirect(url_for('app_auth.edit_profile', user=current_user, user_name=new_user.user_name))

    return render_template('sign_up.html', user=current_user)


@app_auth.route('/log-out')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app_auth.login'))


@app_auth.route('/remove-follower', methods=['POST'])
def remove_follower():
    flwr = json.loads(request.data)
    flwr_id = flwr['flwrId']
    flwr = Follower.query.get(flwr_id)
    if flwr:
        # print(flwr)
        if flwr.user_id == current_user.id:
            db.session.delete(flwr)
            db.session.commit()

            flwg = Following.query.filter_by(following_id=current_user.id, user_id=flwr_id).first()
            db.session.delete(flwg)
            db.session.commit()
        else:
            flash("You cannot remove someone else's follower.", category='error')
    return jsonify({})


@app_auth.route('/unfollow', methods=['POST'])
def unfollow():
    flwg = json.loads(request.data)
    flwg_id = flwg['flwgId']
    flwg = Following.query.get(flwg_id)
    if flwg:
        if flwg.user_id == current_user.id:
            db.session.delete(flwg)
            db.session.commit()

            flwr = Follower.query.filter_by(follower_id=current_user.id, user_id=flwg_id).first()
            db.session.delete(flwr)
            db.session.commit()
        else:
            flash("You cannot manage someone else's following.", category='error')

    return jsonify({})


@app_auth.route('/follow', methods=['POST'])
def follow():
        person = json.loads(request.data)
        person_id = person['personId']
        check_following = Following.query.filter_by(user_id=current_user.id, following_id=person_id).first()
        if check_following:
            return jsonify({})

        new_following = Following(user_id=current_user.id, following_id=person_id)
        db.session.add(new_following)
        db.session.commit()

        new_follower = Follower(user_id=person_id, follower_id=current_user.id)
        db.session.add(new_follower)
        db.session.commit()

        return jsonify({})


@app_auth.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'GET':
        return redirect(url_for('app_views.app_feed'))
    searched = request.form.get('searched')
    return redirect(url_for('app_auth.searched', base64=base64, searched=searched))


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

    return render_template('searched_user.html', lis=found, base64=base64, user=current_user, searched=searched)


@app_auth.route('/<user_name>/create-post', methods=['GET', 'POST'])
@login_required
def create_post(user_name):
    # get the file type of the uploaded file
    if request.method == 'POST':
        file = request.files['image']
        file_type = imghdr.what(file)

        # I am giving  freedom of not putting any title or caption in post if the user wants not to put

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


@app_auth.route("/edit-post-<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = Post.query.filter_by(id=post_id).first()

    if not post:
        flash("No Post Found", category='error')
        return redirect(url_for('app_views.app_feed'))
    if post.user_id != current_user.id:
        flash("You cannot edit this post as you are not the owner", category='error')
        return redirect(url_for('app_views.app_feed'))
    else:
        if request.method == "GET":
            return render_template('edit_post.html', user=current_user, post=post)
        if request.method == "POST":

            title = request.form.get('title')
            caption = request.form.get('caption')

            # updating here
            post.title = title
            post.caption = caption
            post.timestamp = func.now()
            db.session.commit()

            image_data = base64.b64encode(post.img).decode('utf-8')

            return render_template('just_a_post.html',
                                   User=User,
                                   Like=Like, user=current_user,
                                   post_obj=post,
                                   image_data=image_data,
                                   base64=base64)


@app_auth.route("/delete-comment/<int:comment_id>")
@login_required
def delete_comment(comment_id):
    cmnt = Comment.query.filter_by(id=comment_id).first()
    if cmnt:
        if cmnt.commenter != current_user.id and cmnt.post.user_id != current_user.id:
            flash("Sorry! You are neither the commenter nor the owner of post, so you can't delete the comment.",
                  category='error')
        else:
            db.session.delete(cmnt)
            db.session.commit()
    else:
        flash("Comment does not exist.", category='error')
    return redirect(url_for('app_views.app_feed'))


@app_auth.route("/edit-profile/<user_name>", methods=["POST", "GET"])
@login_required
def edit_profile(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if not user:
        flash("User not found", category='error')
        return redirect(url_for('app_views.app_feed'))
    if user.id != current_user.id:
        flash("You cannot edit someone else's profile", category='error')
        return redirect(url_for('app_views.app_feed'))
    else:
        if request.method == "POST":
            name = request.form.get('name')
            about = request.form.get('about')

            user.name = name
            user.about = about

            file = request.files['image']
            file_type = imghdr.what(file)

            if file_type in ['jpeg', 'png']:
                mimetype = file.mimetype
                user.profile_pic = file.read()
                user.mimetype = mimetype

            db.session.commit()


            return render_template("profile.html",
                                   base64=base64,
                                   user=current_user,
                                   user_obj=current_user,
                                   user_name=user.user_name)

        return render_template("edit_profile.html", user=user)


@app_auth.route('/like-post-<post_id>', methods=['POST'])
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


@app_auth.route("/hide-post-<post_id>")
@login_required
def hide_post(post_id):

    post = Post.query.filter_by(id=post_id).first()
    if current_user.id != post.user_id:
        return "Any one other than Author cannot hide the post.", 404
    if post.hide == 0:
        post.hide = 1
        flash('Post hidden Successfully', category='success')
    else:
        post.hide = 0
        flash('Post is visible to others now', category='success')
    db.session.commit()

    return redirect(url_for('app_views.app_feed'))


@app_auth.route("/delete-post-<post_id>", methods=["POST"])
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
        flash("Post Deleted Successfully", category='success')
    return redirect(url_for('app_views.app_feed'))


@app_auth.route("/create-comment/<int:post_id>", methods=['POST'])
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
