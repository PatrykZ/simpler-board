from google.appengine.ext import db

class Comment(db.Model):
    body = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    post_id = db.IntegerProperty(required=True)

    # Decorator for adding new comments
    @classmethod
    def add_comment(cls, body, author, post_id):
        return Comment(body=body, author=author, post_id=post_id)
