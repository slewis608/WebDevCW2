from app import db
from flask_login import UserMixin

roles_users = db.Table('roles_users', db.Column('user_id', db.ForeignKey('users.id')),
                        db.Column('role_id', db.Integer, db.ForeignKey('role.id')))


class users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500), index=True, unique=True)
    email = db.Column(db.String(500), index=True, unique=True)
    runs = db.relationship('runs', backref='users', lazy='dynamic')
    password = db.Column(db.String(250))
    active = db.Column(db.Boolean)
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


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

    def __repr__(self):
        return '{}{}{}{}'.format(self.runId, self.runTitle, self.run_dateTime, self.runDistance)

