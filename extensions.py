#Import external packages and create external objects
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import flask


migrate = Migrate()
db = SQLAlchemy()
login_manager = LoginManager()
