from re import L
from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, PasswordField, SubmitField, BooleanField, DecimalField, DateTimeLocalField, TextAreaField
from wtforms.validators import DataRequired, InputRequired

class registerForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmPassword = PasswordField('Confirm Password', validators=[DataRequired()])
    submitRegistration = SubmitField('Register')

class loginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

class newRunForm(FlaskForm):
    runTitle = StringField('Title', validators=[DataRequired()])
    runDistance = DecimalField('Distance (km)', places=2, rounding=None)
    runDate = DateTimeLocalField('Date & Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    runDesc = TextAreaField('Description', validators=[InputRequired()])
    submitRun = SubmitField('Post Run')

class followForm(FlaskForm):
    followSubmit = SubmitField('Follow')
    unfollowSubmit = SubmitField('Unfollow')

class searchForm(FlaskForm):
    searchField = StringField(validators=[DataRequired()], name='searched')
    submit = SubmitField('Search')