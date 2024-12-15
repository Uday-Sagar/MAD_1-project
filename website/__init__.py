from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import Flask


db=SQLAlchemy()


def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
    app.secret_key='secretkey'

    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    create_database(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    from .models import User
    @login_manager.user_loader
    def load_user(usr_id):
        return User.query.get(int(usr_id))
    
    return app

def create_database(app):
    with app.app_context():
        db.create_all()
    print("database created !!")