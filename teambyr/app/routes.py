from __future__ import print_function
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_sqlalchemy import sqlalchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import secrets, os, time, sys
from app import app, db, images
from app.forms import RegistrationForm, LoginForm, SortMyMovieForm, NewMovieForm, ProfileForm, SearchForm, DiscussionForm, WallForm, EditProfileForm
from app.models import User, Movie, Genre, MoviePoster, Post, Watchlist, Watchedlist
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from PIL import Image

@app.before_first_request
def initDB(*args, **kwargs):
	db.create_all()
	if Genre.query.count() == 0:
		genres = ['action', 'romance', 'comedy']
		for t in genres:
			db.session.add(Genre(name=t))
		db.session.commit()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = SortMyMovieForm()
	movies = db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id)))
	watched = db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id)))
	if Movie.query.first() is None:
		recommended = db.session.query(Movie).filter(~Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id)))
	else:
		recommended = db.session.query(Movie).filter(~Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).order_by(Movie.postNum.desc()).first()
		if recommended is None:
			recommended = db.session.query(Movie).order_by(Movie.postNum.desc()).first()
	if request.method == 'POST':
		sorting = int(form.select.data)
		if (sorting == 1):
			movies = db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id)))
			watched = db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id)))
		elif (sorting == 2):
			movies = db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Action")))
			watched = db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Action")))
		elif (sorting == 3):
			movies = db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Comedy")))
			watched = db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Comedy")))
		elif (sorting == 4):
			movies = db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Romance")))
			watched = db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).filter(Movie.genres.any(Genre.name.contains("Romance")))
	if Movie.query.first() is None:
		return render_template('index.html', title='My Movies', movies=movies, form=form, watched=watched, recommended=recommended)
	else:
		return render_template('index.html', title='My Movies', movies=movies, form=form, watched=watched, recommended=[recommended])

@app.route('/upVote/<movie_id>', methods=['GET'])
@login_required
def upVote(movie_id):
    myupVote = Movie.query.filter_by(id=movie_id).first_or_404()
    myupVote.upVotes = myupVote.upVotes+1
    db.session.add(myupVote)
    db.session.commit()
    movies = Movie.query.order_by(Movie.id.desc())
    return redirect(request.referrer)

@app.route('/downVote/<movie_id>', methods=['GET'])
@login_required
def downVote(movie_id):
    mydownVote = Movie.query.filter_by(id=movie_id).first_or_404()
    mydownVote.downVotes = mydownVote.downVotes+1
    db.session.add(mydownVote)
    db.session.commit()
    movies = Movie.query.order_by(Movie.id.desc())
    return redirect(request.referrer)


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('You have successfully registered!')
		return redirect(url_for('login'))
	return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is None or not user.get_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))	
		login_user(user, remember=form.remember_me.data)
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
	form = SearchForm()
	movies = db.session.query(Movie)
	if form.validate_on_submit():
		searching = (form.search.data)
		movies = db.session.query(Movie).filter(Movie.title.contains(searching))
	return render_template('search.html', title='search', form=form, movies=movies)

@app.route('/newMovie', methods=['GET', 'POST'])
@login_required
def newMovie():
	form = NewMovieForm()
	if form.validate_on_submit():
		image = request.files['image']
		if image.filename == "":
			print("image must have a filename")
			return redirect(request.url)
		filename = secure_filename(image.filename)
		image.save(os.path.join(app.config['UPLOADED_IMAGES_DEST'], filename))
		url = filename
		newMovie = Movie(title = form.title.data, description = form.description.data, genres = form.genres.data, image_id = url, user_id = current_user.id)	
		db.session.add(newMovie)
		db.session.commit()
		flash('Your movie has been created!')
		return redirect(url_for('index'))
	return render_template('newMovie.html', title='new movie', form=form)

@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	picture = url_for('static', filename=current_user.picture_id)
	posts = db.session.query(Post).filter(Post.user_name.contains(username))
	return render_template('user.html', user=user, picture=picture, posts=posts)

@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen=datetime.utcnow()
		db.session.add(current_user)
		db.session.commit()

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
	form = EditProfileForm()
	if form.validate_on_submit():
		current_user.about_me = form.about_me.data
		current_user.username = form.username.data
		db.session.commit()		
		flash('Saved!')
		return redirect(url_for('user', username=current_user.username, form=form))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('profile.html', title='Edit Profile', form=form)

# might delete...idk if we really need this anymore
#@app.route('/table', methods=['GET', 'POST'])
#@login_required
#def table():
#	users = User.query.all()
#	return render_template('table.html', users=users)

@app.route('/wall', methods=['GET', 'POST'])
def wall():
	form = WallForm()
	if request.method == 'POST':
		if form.password.data == "cherry":
			return redirect(url_for('register_admin'))
	return render_template('wall.html', form=form)

@app.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data, is_admin = True)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash("Admin account has been successfully created")
		return redirect(url_for('login')) 
	return render_template('admin_register.html', form=form)

@app.route('/discussion/<movieid>', methods=['GET', 'POST'])
@login_required
def discussion(movieid):
	form = DiscussionForm()
	movie = Movie.query.filter_by(id=movieid).first()
	posts = Post.query.filter_by(movie_id=movieid)
	if movie is None:
		flash('Movie with id "{}" not found'.format(movieid))
		return redirect(url_for('index'))
	if form.validate_on_submit():
		if request.form['action'] == "post":
			newPost = Post(user_name = current_user.username, body=form.body.data, movie_id=movieid, movie_title=movie.title)
			postNum = movie
			postNum.postNum = postNum.postNum+1
			db.session.add(postNum)
			db.session.add(newPost)
			db.session.commit()
			return redirect(url_for('discussion', movieid=movieid))
		elif request.form['action'] == "Add to To-Watch List":
			if db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id))).filter(Movie.watchlist.any(Watchlist.movie_id.contains(movieid))).first() is None:
				if db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).filter(Movie.watchedlist.any(Watchedlist.movie_id.contains(movieid))).first():
					Watchedlist.query.filter_by(user_id = current_user.id, movie_id=movieid).delete()
					db.session.commit()
				watchlist = Watchlist(user_id = current_user.id, movie_id=movieid)
				db.session.add(watchlist)
				db.session.commit()
				return redirect(url_for('index'))
			else:
				flash('The movie is already in your To-Watch List')
		elif request.form['action'] == "Remove from To-Watch List":
			Watchlist.query.filter_by(user_id = current_user.id, movie_id=movieid).delete()
			db.session.commit()
			return redirect(url_for('index'))
		elif request.form['action'] == "Add to Watched List":
			if db.session.query(Movie).filter(Movie.watchedlist.any(Watchedlist.user_id.contains(current_user.id))).filter(Movie.watchedlist.any(Watchedlist.movie_id.contains(movieid))).first() is None:
				if db.session.query(Movie).filter(Movie.watchlist.any(Watchlist.user_id.contains(current_user.id))).filter(Movie.watchlist.any(Watchlist.movie_id.contains(movieid))).first():
					Watchlist.query.filter_by(user_id = current_user.id, movie_id=movieid).delete()
					db.session.commit()
				watchedlist = Watchedlist(user_id = current_user.id, movie_id=movieid)
				db.session.add(watchedlist)
				db.session.commit()
				return redirect(url_for('index'))
			else:
				flash('The movie is already in your Watched List')
		elif request.form['action'] == "Remove from Watched List":
			Watchedlist.query.filter_by(user_id = current_user.id, movie_id=movieid).delete()
			db.session.commit()
			return redirect(url_for('index'))
		elif request.form['action'] == "Delete Movie":
			Watchedlist.query.filter_by(movie_id=movieid).delete()
			Watchlist.query.filter_by(movie_id=movieid).delete()
			db.session.delete(movie)
			db.session.commit()
			flash("The movie has been deleted")
			return redirect(url_for('index'))
		else:
			flash('failure')
	return render_template('discussion.html', title='discussion', form=form, movie=movie, posts=posts)