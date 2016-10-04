import cgi

from google.appengine.ext import db
from like import Like
from comment import Comment
from app.utils.render import *


class Post(db.Model):
    # Database parameters for the Post object
    title = db.StringProperty(required=True)
    post = db.TextProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    author = db.StringProperty()

    # Decorator that returns an instance of Post object containing information
    # about the title, body and author of the post
    @classmethod
    def add_post(cls, title, body, author):
        body_escaped = cgi.escape(str(body))
        return Post(title=title, post=body_escaped, author=author)

    @classmethod
    def by_id(cls, post_id):
        cls.get_by_id(int(post_id))

    # Function that takes the instance of the post and replaces the
    # breaks with <br>
    def render(self):
        self._render_text = self.post.replace('\n', '<br>')
        post_id = self.key().id()

        likes = Like.all().filter('post_id =', int(post_id))
        comments = Comment.all().filter('post_id =', int(post_id))

        return render_str("post.html", post=self, likes=likes,
                          comments=comments)
