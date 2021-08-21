from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app import db, login, admin
from hashlib import md5
from werkzeug.exceptions import abort

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

def load_image(id):
    return MoviePoster.query.get(int(id))

genres = db.Table('genres', 
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True), 
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String())
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)

class Watchedlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String())
    movie_id = db.Column(db.Integer, db.ForeignKey("movie.id"), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())

class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), index=True)
    description = db.Column(db.String(1500))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    genres = db.relationship('Genre', secondary=genres, lazy='subquery', backref=db.backref('movies', lazy=True))
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'))
    watchlist = db.relationship("Watchlist", backref='movie', lazy=True)
    watchedlist = db.relationship("Watchedlist", backref='movie', lazy=True)
    upVotes = db.Column(db.Integer, default = 0)
    downVotes = db.Column(db.Integer, default = 0)
    postNum = db.Column(db.Integer, default = 0)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(150))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    picture_id = db.Column(db.Integer, db.ForeignKey('profile_picture.id'), default = 'default.png')

    def __repr__(self):
        return '<User {} - {} - {}>'.format(self.id, self.username, self.picture) 

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_password(self, password):
        return check_password_hash(self.password_hash, password)

class ProfilePicture(db.Model):
    __tablename__ = 'profile_picture'
    id = db.Column(db.Integer, primary_key=True)
    picture = db.Column(db.Text, unique=True, nullable=False, default='default.png')
    picture_type = db.Column(db.Text, nullable=False)
    user = db.relationship('User', uselist=False, backref='profile_picture')

class Admin(ModelView):
    def is_accessible(self):
        if current_user.is_admin == True:
            return current_user.is_authenticated
        else:
            return abort(404)
    def not_authenticated(self):
        return "Admin access only"

admin.add_view(Admin(User, db.session))

class MoviePoster(db.Model):
    __tablename__ = 'image'
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text, unique=True, nullable=False)
    img_type = db.Column(db.Text, nullable=False)
    movie = db.relationship('Movie', uselist=False, backref='image')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String, db.ForeignKey('user.username'))
    movie_title = db.Column(db.Integer, db.ForeignKey('movie.title'))
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'))
    body = db.Column(db.String())