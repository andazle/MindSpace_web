from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import pytz

db = SQLAlchemy()

def novosibirsk_time():
    """Возвращает текущее время в часовом поясе Новосибирска"""
    tz = pytz.timezone('Asia/Novosibirsk')
    return datetime.now(tz)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=novosibirsk_time)

    checkups = db.relationship('Checkup', backref='user', lazy='dynamic')
    journal_entries = db.relationship('JournalEntry', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Checkup(db.Model):
    __tablename__ = 'checkups'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=novosibirsk_time)

    stress = db.Column(db.Integer)
    sleep = db.Column(db.Integer)
    energy = db.Column(db.Integer)
    focus = db.Column(db.Integer)
    satisfaction = db.Column(db.Integer)
    motivation = db.Column(db.Integer)
    social = db.Column(db.Integer)
    nutrition = db.Column(db.Integer)
    hopes = db.Column(db.Integer)
    control = db.Column(db.Integer)

class JournalEntry(db.Model):
    __tablename__ = 'journal_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, default=novosibirsk_time)
    text = db.Column(db.Text, nullable=False)