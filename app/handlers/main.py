import webapp2

from app.utils.render import *
from app.models.user import *
from google.appengine.ext import db
from app.models.post import *

# Main handler
class Handler(webapp2.RequestHandler):
    # Helper functions
    def write(self, *a, **params):
        self.response.out.write(*a, **params)

    # Generates entire html
    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    # Writes the generated html onto the webpage
    def render(self, template, **params):
        self.write(self.render_str(template, **params))

    # Requests cookie from the client
    def get_cookie(self, name):
        return self.request.cookies.get(str(name))

    # Sets secure coookie inside client, made out of name and hash,
    # for ex. james | skdoskdoskdos

    def set_secure_cookie(self, name, value):
        self.response.headers.add_header('Set-Cookie', '%s=%s; Path=/' % (
            name, str(hash_item(value))))

    # Takes the cookie and runs it through check_hash_item function that checks
    # if the cookie has a proper hash value

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_hash_item(cookie_val)

    # Retrieves the post key from the url
    def get_post_key(self, post_id):
        return db.Key.from_path('Post', int(post_id))

    # Retrieves the post key from the url
    def get_comment_key(self, post_id):
        return db.Key.from_path('Comment', int(post_id))

    # Overrides the default function on every page
    def initialize(self, *a, **kw):
        # Take the initial conftent of initialize function and pass it in
        webapp2.RequestHandler.initialize(self, *a, **kw)

        # Checks for secure cookie of username
        username = self.read_secure_cookie('username')

        # If proper username has been found in the cookie, store the instance
        # of User object inside the self.user variable
        self.user = username and User.by_name(username)
