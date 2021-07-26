from datetime import timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restful import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = '4576c836be2d7d51f727e01745901904'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<<username>>:<<password>>@<<ip address>>/<<database_name>>'
db = SQLAlchemy(app)
# db.init_app(app)
# migrate = Migrate(app, db)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "100 per hour"]
)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from healthapp.webapp import routes
from healthapp.restapi import resources
