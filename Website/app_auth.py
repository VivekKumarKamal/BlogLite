from flask import Blueprint, render_template, flash, redirect, url_for, request
from .app_models import User, Post, Like, Comment, Following, Follower, db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, select, exc
from . import DB_NAME
import sqlite3

engine = create_engine(f"sqlite:///./{DB_NAME}")
app_auth = Blueprint('app_auth', __name__)



@app_auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form.get('user_name')
        password = request.form.get('password')

        user = User.query.filter_by(user_name=user_name).first()


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
            flash("Passwords don't match")
            # print("not matched")
        elif len(password) < 3:
            flash("Password is too short, should be greater than 7 characters")

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
    # with Session(engine) as session:
    #     follower_lis = session.execute(select(Follower.follower_id).where(Follower.user_id == id)).all()
    #
    #
    #     # us = follower.query.filter_by(user_id=1).all()
    #     print(follower_lis)
    user = User.query.filter_by(user_name=user_name).first()

    # follower_user_names = []
    # for a in user.followers:
    #     name = User.query.filter_by(id=a.follower_id).first()
    #     follower_user_names.append(name)

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
        return render_template('profile_page.html', user_name=user_name, name=user.name,flwr_count=flwr_count, flwg_count=flwg_count, user=current_user)
    else:
        return "This user does not exist"

@app_auth.route('/log-out')
@login_required
def logout():
    logout_user()
    return redirect(url_for('app_auth.login'))

@app_auth.route('/remove-follower/<follower>', methods=['POST'])
def remove_follower(flwr):
    flwr = int(flwr)
    id = Follower.query.get(follower_id=flwr)
