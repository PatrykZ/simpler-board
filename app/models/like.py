from google.appengine.ext import db

class Like(db.Model):
    liked = db.BooleanProperty(default=False)
    post_id = db.IntegerProperty(required=True)
    author = db.StringProperty(required=True)

    # Decorator for adding likes
    @classmethod
    def add_like(cls, liked, author, post_id):
        return Like(liked=liked, author=author, post_id=post_id)
