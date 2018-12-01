from sqlalchemy import Column, String
from flask_login import UserMixin

class User(UserMixin):
    username = Column(String(100), primary_key=True)
    password = Column(String(50))

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    def __repr__(self):
        return '<User %r>' % (self.username)
