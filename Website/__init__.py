from flask import Flask
from flask_restful import Resource, Api

from flask_sqlalchemy import SQLAlchemy
from markupsafe import escape
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = 'mini_insta_database.sqlite3'


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "It's Vivek"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    api = Api(app)

    login_manager = LoginManager()
    login_manager.login_view = 'app_auth.login'
    login_manager.login_message = u"Log in to access the page"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    from .app_views import app_views
    from .app_auth import app_auth

    app.register_blueprint(app_views, url_prefix='/')
    app.register_blueprint(app_auth, url_index='/')

    from .app_models import User, Post, Like, Comment, Following, Follower

    with app.app_context():
        db.create_all()

    return app, api
