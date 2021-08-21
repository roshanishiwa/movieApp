import os
basedir = os.path.abspath(os.path.dirname(__file__))
TOP_LEVEL_DIR = os.path.abspath(os.curdir)

class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-not-guess-this'
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
		'sqlite:///' + os.path.join(basedir, 'movie.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	UPLOADS_DEFAULT_DEST = TOP_LEVEL_DIR + '/app/static/'
	UPLOADS_DEFAULT_URL = 'http://localhost:5000/static/'
	UPLOADED_IMAGES_DEST = TOP_LEVEL_DIR + '/app/static/'
	UPLOADED_IMAGES_URL = 'http://localhost:5000/static/'

class TestConfig(object):
	SECRET_KEY = 'bad-bad-key'
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	WTF_CSRF_ENABLED = False
	DEBUG = True
	TESTING = True