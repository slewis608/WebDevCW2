from flask import render_template, request, url_for, redirect
from app import app, db, models
from flask_security import Security, SQLAlchemyUserDatastore, current_user, auth_required, login_required
from flask_security.utils import hash_password, verify_password, login_user
from .forms import registerForm, loginForm, newRunForm
from .models import users, runs
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, desc

user_datastore = SQLAlchemyUserDatastore(db, models.users, models.Role)
security = Security(app, user_datastore)

def find_total_runs(thisUser):
    return len(models.runs.query.filter_by(user_Id=thisUser.id).all())

def calc_monthly_distance(thisUser):
    monthAgo = datetime.today() - timedelta(days=28)
    print(monthAgo)
    userRuns = models.runs.query.filter_by(user_Id=thisUser.id).all()
    print(userRuns)
    distanceThisMonth = []
    totalRuns = 0
    for i in userRuns:
        if (i.run_dateTime <= datetime.today()) and (i.run_dateTime >= monthAgo ):
            distanceThisMonth.append(i.runDistance)
            totalRuns+=1

    return {'numRuns': totalRuns, 'distRuns': sum(distanceThisMonth)}

def get_posts(postArr):
    postDictArr = []
    for post in postArr:
        postDict = {}
        postDict['username'] = users.query.get(post.user_Id).username
        postDict['date'] = post.run_dateTime.strftime("%d/%m/%Y, %H:%M")
        postDict['title'] = post.runTitle
        postDict['distance'] = post.runDistance
        postDict['description'] = post.runDescription
        postDictArr.append(postDict)
    return postDictArr



@app.route('/delpost/<postId>', methods=['POST'])
def delPost():
    pass


@app.route('/')
def redirecting():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))



@app.route('/home', methods=['POST', 'GET'])
def index():
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    form = newRunForm()
    userName = current_user.username
    if form.validate_on_submit():
        userName = 'TEST'
        theUser = current_user.id
        runPost = models.runs(user_Id = theUser, runTitle=form.runTitle.data, 
                    runDistance=form.runDistance.data, run_dateTime=form.runDate.data, runDescription=form.runDesc.data)
        db.session.add(runPost)
        db.session.commit()
        return redirect(url_for('index'))
    totalRuns = find_total_runs(current_user)
    distanceThisMonth = calc_monthly_distance(current_user)['distRuns']
    runsThisMonth = calc_monthly_distance(current_user)['numRuns']
    print(calc_monthly_distance(current_user))
    allPostsOrdered = get_posts(models.runs.query.order_by(desc(runs.run_dateTime)).all())
    return render_template('home.html', title="Homepage", navbarOn = True, userName = userName, form=form, totalRuns=totalRuns,
            distanceThisMonth=distanceThisMonth, runsThisMonth=runsThisMonth, allPostsOrdered = allPostsOrdered)

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
    return render_template('profile.html', title = 'Profile', navbarOn = True)

@app.route('/explore')
def explore():
    return render_template('explore.html', title = 'Explore', navbarOn = True)

@app.route('/myruns')
def myruns():
    # Get all runs assigned to this user.
    userPosts = get_posts(models.runs.query.filter_by(user_Id = current_user.id).order_by(desc(runs.run_dateTime)).all())
    print(userPosts)

    return render_template('myruns.html', title = 'My Runs', navbarOn = True, userPosts = userPosts)