from app import db
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
roles_users = db.Table('roles_users', db.Column('user_id', db.ForeignKey('users.id')),
                        db.Column('role_id', db.Integer, db.ForeignKey('role.id')))

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('users.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('users.id'),
              primary_key=True)
)


class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), index=True, unique=True)
    email = db.Column(db.String(500), index=True, unique=True)
    runs = db.relationship('runs', backref='users', lazy='dynamic')
    password = db.Column(db.String(250))
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    following: so.WriteOnlyMapped['users'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    followers: so.WriteOnlyMapped['users'] = so.Relationship(
        secondary=followers, primaryjoin = (followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')
    
    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        query = self.following.select().where(users.id == user.id)
        return db.session.scalar(query) is not None

    def __repr__(self):
        return '{}{}{}'.format(self.id, self.username, self.email)

class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(500))


class runs(db.Model):
    runId = db.Column(db.Integer, primary_key=True)
    user_Id = db.Column(db.Integer, db.ForeignKey('users.id'))
    runTitle = db.Column(db.String(500), index=True)
    runDistance = db.Column(db.Float)
    run_dateTime = db.Column(db.DateTime)
    runDescription = db.Column(db.String(500))

    def __repr__(self):
        return '{}{}{}{}'.format(self.runId, self.runTitle, self.run_dateTime, self.runDistance)
