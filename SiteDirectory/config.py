import os
from flask import url_for
WTF_CSRF_ENABLED = True
SECRET_KEY = 'the-very-big-secret'
basedir = os.path.abspath(os.path.dirname(__file__))
SECURITY_LOGIN_URL = '/foaijdjk'
SECURITY_POST_LOGIN_VIEW = '/home'
SECURITY_POST_LOGOUT_VIEW = '/login'
SECURITY_UNAUTHORIZED_VIEW = '/logout'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECURITY_PASSWORD_SALT = 'theSecretSalt'