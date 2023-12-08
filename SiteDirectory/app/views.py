from flask import render_template, request, url_for, redirect
from app import app, db, models
from flask_security import Security, SQLAlchemyUserDatastore, current_user, login_required
from flask_security.utils import hash_password, verify_password, login_user
from .forms import registerForm, loginForm
from .models import users

user_datastore = SQLAlchemyUserDatastore(db, models.users, models.Role)
security = Security(app, user_datastore)

@app.route('/home')
@login_required
def index():
    if not(current_user.is_authenticated):
        return redirect(url_for('/login'))
    return render_template('home.html', title="Homepage", navbarOn = True)

@app.route('/login', methods=['POST', 'GET'])
def login():
    form = loginForm()
    if current_user.is_authenticated:
       return redirect(url_for('index'))
    if request.method == 'POST':
        if form.validate_on_submit():
            userAttempt = models.users.query.filter_by(email=form.email.data).all()
            if len(userAttempt) > 0:
                userObj = userAttempt[0]
                if verify_password(form.password.data, userObj.password):
                    login_user(userObj)
                    return redirect(url_for('index'))
                else:
                    return redirect(url_for('register'))
    return render_template('login.html', form=form)
        

@app.route('/register', methods=['POST','GET'])
def register():
    form = registerForm()
    if request.method == 'POST':
        user_datastore.create_user(
            username = request.form.get('username'),
            email = request.form.get('email'),
            password = hash_password(request.form.get('password'))
        )
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('registration.html', form=form)

@app.route('/profile')
def profile():
    return render_template('profile.html')