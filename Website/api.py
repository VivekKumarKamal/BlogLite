# ERROR: NO API For Blogs

# from main import app
from flask import Blueprint, render_template, flash, request, jsonify, redirect, url_for, app
from flask_login import login_required, current_user
from . import db
from .app_models import User, Post, Like, Comment, Following, Follower, db, SearchForm
import imghdr


api = Blueprint('api', __name__)


import jwt
from functools import wraps

# @api.route('/api/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     user_name = data['user_name']
#     password = data['password']
#     user = User.query.filter_by(user_name=user_name).first()
#
#     if user and user.password == password:
#
#         from main import app
#
#         token = jwt.encode({'user_id': user.id}, app.config['SECRET_KEY'])
#         return jsonify({'token': token.decode('UTF-8')})
#     else:
#         return jsonify({'message': 'Invalid credentials'}), 401
#
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('x-access-token')
#         if not token:
#             return jsonify({'message': 'Token is missing!'}), 401
#         try:
#             data = jwt.decode(token, app.config['SECRET_KEY'])
#         except:
#             return jsonify({'message': 'Token is invalid!'}), 401
#         return f(*args, **kwargs)
#     return decorated


@api.route('/api/user/<user_name>', methods=['GET'])
def get_user(user_name):
    user_obj = User.query.filter_by(user_name=user_name).first()
    if user_obj:
        return jsonify(user_obj.to_dict()), 200
    else:
        return "This user does not exist", 404


@api.route('/api/user', methods=['POST'])
def create_user():
    data = request.get_json()
    name = data['name']
    user_name = data['user_name']
    password = data['password']

    if len(password) < 3:
        return "Password should be more than 2 characters", 400

    user = User.query.filter_by(user_name=user_name).first()
    if user:
        return "UserName already exists, please choose another or try adding numbers in user_name", 403

    user = User(name=name, user_name=user_name, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@api.route('/api/user/<user_name>', methods=['PUT'])
def update_user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        data = request.get_json()

        user.name = data['name']
        user.about = data['about']

        file = data['image']
        file_type = imghdr.what(file)

        if file_type in ['jpeg', 'png']:
            mimetype = file.mimetype
            user.profile_pic = file.read()
            user.mimetype = mimetype

        db.session.commit()
        return jsonify(user.to_dict()), 200
    else:
        return jsonify({"message": "user not found"}), 404


@api.route('/api/user/<user_name>', methods=['DELETE'])
def delete_user(user_name):
    user = User.query.filter_by(user_name=user_name).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "user deleted"}), 200
    else:
        return jsonify({"message": "user not found"}), 404


@api.route('/api/blog/<blog_id>', methods=['GET'])
def get_blog(blog_id):
    try:
        blog_id = int(blog_id)
    except ValueError:
        return jsonify({"message": "Invalid blog_id, it should be a number"}), 400
    blog_obj = Post.query.filter_by(id=blog_id).first()
    if blog_obj:
        return jsonify(blog_obj.to_dict()), 200
    else:
        return jsonify({"message": "This blog does not exist"}), 404



@api.route('/api/blog', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data['title']
    caption = data['caption']
    img = data['img']
    mimetype = data['mimetype']
    user_id = data['user_id']

    new_post = Post(title=title, caption=caption, img=img, mimetype=mimetype, user_id=user_id)
    db.session.add(new_post)
    db.session.commit()

    return jsonify({'message': 'Post created successfully!'}), 201


@api.route('/api/blog/<int:id>', methods=['PUT'])
def update_post(id):
    post = Post.query.get(id)
    if post:
        data = request.get_json()
        post.title = data['title']
        post.caption = data['caption']
        post.img = data['img']
        post.mimetype = data['mimetype']
        post.user_id = data['user_id']
        db.session.commit()
        return jsonify({'message': 'Post updated successfully!'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404


@api.route('/api/blog/<int:id>', methods=['DELETE'])
def delete_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully!'}), 200
    else:
        return jsonify({'message': 'Post not found'}), 404
