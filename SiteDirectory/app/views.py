from flask import render_template, request, url_for, redirect
from app import app, db, models
from flask_security import Security, SQLAlchemyUserDatastore, current_user, auth_required, login_required
from flask_security.utils import hash_password, verify_password, login_user
from .forms import registerForm, loginForm, newRunForm, searchForm
from .models import users, runs, followers
from flask_login import current_user
from datetime import datetime, timedelta
from sqlalchemy import and_, desc, select
import json

user_datastore = SQLAlchemyUserDatastore(db, models.users, models.Role)
security = Security(app, user_datastore)

def find_total_runs(thisUser):
    return len(models.runs.query.filter_by(user_Id=thisUser.id).all())

def calc_monthly_distance(thisUser):
    monthAgo = datetime.today() - timedelta(days=28)
    userRuns = models.runs.query.filter_by(user_Id=thisUser.id).all()
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
        postDict['id'] = post.runId
        postDict['userId'] = post.user_Id
        postDictArr.append(postDict)
    return postDictArr



@app.route('/delpost/<post_id>', methods=['POST'])
def delPost(post_id):
    runs.query.filter_by(runId = post_id).delete()
    db.session.commit()
    return redirect(url_for('myruns'))



@app.route('/follow', methods=['POST'])
def vote():
    # Load JSON data and use the ID of the user that was clicked to get the object
    data = json.loads(request.data)
    user_id = int(data.get('user_id'))
    thisUserObj = users.query.filter_by(id=user_id).all()[0]
    if data.get('followUnfollow') == "follow":
        current_user.follow(thisUserObj)
    else:
        current_user.unfollow(thisUserObj)
    db.session.commit()
    # Tell the JS .ajax() call the data was processed OK
    return json.dumps({'status': 'OK'})
    
    




@app.route('/')
def redirecting():
    db.session.commit()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))
    

def getFollowerPosts():

        # Get user's followers
        stmt = (select(runs).select_from(runs).join(
                followers, followers.c.followed_id == runs.user_Id)
                .filter_by( follower_id = current_user.id)).order_by(desc(runs.run_dateTime))
        x = (db.session.execute(stmt))
        arrFollowerRuns = []
        for i in x.scalars():
            dictRun = {}
            dictRun['runId'] = i.runId
            dictRun['username'] = models.users.query.get(i.user_Id).username
            dictRun['title'] = i.runTitle
            dictRun['distance'] = i.runDistance
            dictRun['description'] = i.runDescription
            dictRun['Date'] = i.run_dateTime.strftime("%d/%m/%Y %H:%M")
            arrFollowerRuns.append(dictRun)
        return arrFollowerRuns
            



@app.route('/home', methods=['POST', 'GET'])
def index():
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    form = newRunForm()
    userName = current_user.username
    if form.validate_on_submit():
        theUser = current_user.id
        runPost = models.runs(user_Id = theUser, runTitle=form.runTitle.data, 
                    runDistance=form.runDistance.data, run_dateTime=form.runDate.data, runDescription=form.runDesc.data)
        db.session.add(runPost)
        db.session.commit()
        return redirect(url_for('index'))
    totalRuns = find_total_runs(current_user)
    distanceThisMonth = calc_monthly_distance(current_user)['distRuns']
    runsThisMonth = calc_monthly_distance(current_user)['numRuns']
    allPostsOrdered = getFollowerPosts()
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
        return redirect(url_for('login'))
    return render_template('registration.html', form=form)

# View for other users' profile
@app.route('/user/<user_name>')
def otherProfile(user_name):
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    # If user is attempting to access his own account, redirect to '/myruns'
    if current_user.username == user_name:
        return redirect(url_for('myruns'))
    # Check if user is following this user to choose whether to display follow or unfollow button
    userObj = models.users.query.filter_by(username=user_name).first()
    followButtonOn = True
    if current_user.is_following(userObj):
        followButtonOn = False
    userThisMonth = calc_monthly_distance(userObj)
    userPosts = get_posts(models.runs.query.filter_by(user_Id=userObj.id).all())
    userHasPosted=True
    if len(userPosts) == 0:
        userHasPosted=False
    return render_template('otheruser.html', title=user_name, navbarOn=True, userPosts = userPosts, userThisMonth = userThisMonth, followButtonOn = followButtonOn, username = userObj.username, userId=userObj.id, userHasPosted=userHasPosted)


def get_user_summaries(userQuery):
    # Build dict of each user's data
    # Obtain most recent post of each user
    dictArr = []
    for userAcc in userQuery:
        userDict = {}
        userDict['username'] = userAcc.username
        # Get user details via their posts
        userDict['totalRuns'] = find_total_runs(userAcc)
        lastRun = models.runs.query.filter_by(user_Id=userAcc.id)
        if len(lastRun.all()) == 0:
            userDict['dateLastRun'] = "No runs found"
        else:
            # lastRun = runs.query.filter_by(user_Id=userAcc.id).order_by(desc(runs.run_dateTime)).all()[0]
            userDict['dateLastRun'] = lastRun.order_by(desc(runs.run_dateTime)).first().run_dateTime.strftime("%d/%m/%Y, %H:%M")
        dictArr.append(userDict)
    return dictArr


@app.route('/explore', methods=['GET','POST'])
def explore():
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    form = searchForm()
    userQuery = users.query
    searchDict = []
    if form.validate_on_submit():
        searchedText = form.searchField.data
        # Query users db to find users
        userQuery = userQuery.filter(users.username.like('%' + searchedText + '%'))
        userQuery = userQuery.order_by(users.username).all()
        searchDict = get_user_summaries(userQuery)
        return render_template('explore.html', title = 'Explore', navbarOn = True, form=form, searchDict=searchDict)
    return render_template('explore.html', title = 'Explore', navbarOn = True, form=form)




@app.route('/myruns')
def myruns():
    if not(current_user.is_authenticated):
        return redirect(url_for('login'))
    # Get all runs assigned to this user.
    userPosts = get_posts(models.runs.query.filter_by(user_Id = current_user.id).order_by(desc(runs.run_dateTime)).all())
    noPosts=False
    if len(userPosts) == 0:
        noPosts=True
    getFollowerPosts()

    return render_template('myruns.html', title = 'My Runs', navbarOn = True, userPosts = userPosts, noPosts = noPosts)
