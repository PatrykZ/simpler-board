from google.appengine.ext import db
from app.utils.hashing import *

class User(db.Model):
    # Database parameters for the User object
    username = db.StringProperty(required=True)
    password = db.StringProperty(required=True)
    email = db.StringProperty()

    # Decorator that gets the instance of User object by id from the db
    @classmethod
    def by_id(cls, user_id):
        return cls.get_by_id(user_id)

    # Decorator that gets the instance of User object by name from the db
    @classmethod
    def by_name(cls, user_id):
        return cls.all().filter('username =', user_id).get()

    # Decorator that creates an instance of User object with hashed password
    @classmethod
    def register(cls, name, pw, email=None):
        hashed_password = make_pw_hash(name, pw)
        return User(username=name,
                    password=hashed_password,
                    email=email)
