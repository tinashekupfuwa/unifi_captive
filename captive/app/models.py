from datetime import datetime
from flask_login import UserMixin
from captive.app import db, login

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mac = db.Column(db.String(17), index=True, unique=True)
    auth = db.relationship('Auth', backref='auth', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.mac) 

    def is_active(self):
    	return True



class Auth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(10))
    pin = db.Column(db.String(6))
    ap_mac = db.Column(db.String(17))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    logged_in = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Pin {}>'.format(self.pin)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

