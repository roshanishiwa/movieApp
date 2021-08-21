from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_uploads import UploadSet, IMAGES, configure_uploads

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
admin= Admin(app, name='Control Panel')
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

from app import routes, models


