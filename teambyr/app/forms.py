from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.ext.sqlalchemy.fields import QuerySelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models import User, Movie, Genre, MoviePoster
from wtforms.widgets import CheckboxInput, ListWidget, Select
from flask_wtf.file import FileField, FileAllowed, FileRequired

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), 
		EqualTo('password')])
	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('The username aready exists. Please choose a different username!')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None: 
			raise ValidationError('The email aready exists. Please use a different email address!')

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')

class SortMyMovieForm(FlaskForm):
	select = SelectField('Sort by:', choices = [(1, "All"), (2, "Action"), (3, "Comedy"), (4, "Romance")])
	submit = SubmitField('Sort')

class SearchForm(FlaskForm):
	search = StringField('Search', validators=[DataRequired()])
	submit = SubmitField('Search')

def get_genres():
	return Genre.query

class NewMovieForm(FlaskForm):
	title = StringField('Title', validators=[DataRequired()])
	genres = QuerySelectMultipleField('Select genres', 
		query_factory = get_genres, get_label = 'name',
		widget = ListWidget(prefix_label=False), 
		option_widget=CheckboxInput() )
	description = StringField('Description')
	image = FileField(validators=[FileRequired()])
	add = SubmitField('Create new movie')

class ProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Update')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('The username aready exists. Please choose a different username!')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None: 
			raise ValidationError('The email aready exists. Please use a different email address!')

class DiscussionForm(FlaskForm):
	body = StringField('Body')
	submit = SubmitField('Post')

class WallForm(FlaskForm):
	password = StringField('Secret Code')
	submit = SubmitField("You're In")

class EditProfileForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	about_me = TextAreaField('About me', validators=[Length(min=0, max=1500)])
	submit = SubmitField('Update')