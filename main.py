#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import cgi

import hashlib
import hmac
import random
from string import letters
import jinja2
import webapp2
from validator import *

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'dist/templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# Secret value for hashing
secret = 'd22j192dj12jd912jds8912dj8'


def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


# Function that generates a hash based on the secret value and returns it
# in a format of value | hash
def hash_item(s):
    return '%s|%s' % (s, hmac.new(secret, s).hexdigest())


# Function that checks if the value that is being passed is correct, by
# comparing it against the make_secure_val() function
def check_hash_item(hash):
    val = hash.split('|')[0]
    if hash == hash_item(val):
        return val


# Function that creates a random string of 5 letters
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


# Function that creates a password hash
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s, %s' % (salt, h)


# Function that checks the hashed password
def check_valid_pw(name, pw, h):
    val = h.split(',')[0]
    if h == make_pw_hash(name, pw, val):
        return h


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


class Homepage(Handler):
    def get(self):
        # Gets all the posts from the database and sorts them
        # from newest to oldest date of submission
        posts = Post.all().order('-date')

        # Renders the homepage along with all the posts
        self.render('homepage.html', posts=posts)


class Comment(db.Model):
    body = db.TextProperty(required=True)
    author = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now_add=True)
    post_id = db.IntegerProperty(required=True)

    # Decorator for adding new comments
    @classmethod
    def add_comment(cls, body, author, post_id):
        return Comment(body=body, author=author, post_id=post_id)


class Like(db.Model):
    liked = db.BooleanProperty(default=False)
    post_id = db.IntegerProperty(required=True)
    author = db.StringProperty(required=True)

    # Decorator for adding likes
    @classmethod
    def add_like(cls, liked, author, post_id):
        return Like(liked=liked, author=author, post_id=post_id)


class AddPost(Handler):
    def get(self):
        # If user is detected then renders addpost.html page,
        # if not then redirects to signup page
        if self.user:
            self.render('addpost.html')
        else:
            self.redirect('/login')

    def post(self):
        if not self.user:
            self.redirect('/')

        # Storing default value for error, if error is detected change to true
        has_error = False

        # Storing values from the user
        self.title = self.request.get('title')
        self.post = self.request.get('post')

        # author_cookie = self.get_cookie('username')
        # self.author = check_hash_item(author_cookie)

        params = dict(title=self.title,
                      post=self.post)

        # Displaying proper error if user input is invalid
        if not self.title:
            params['error_title'] = "Please input post title."
            has_error = True

        if not self.post:
            params['error_post'] = "Post cannot be empty."
            has_error = True

        if has_error:
            self.render('addpost.html', **params)

        else:
            # Creates the instance of a Post object
            post = Post.add_post(self.title, self.post, self.user.username)

            # Sends it to database
            post.put()

            # Redirects the user to a link containing id of the post
            self.redirect('/%s' % str(post.key().id()))


class EditPost(Handler):
    def get(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)

        # Finds and stores the post instance by id from the database
        post_instance = db.get(key)

        if self.user:
            if self.user.username == post_instance.author:
                self.render('editpost.html', post=post_instance)
            else:
                self.redirect('/%s' % str(post_instance.key().id()))
        else:
            self.redirect('/login')

    def post(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)
        # Finds and stores the post instance by id from the database
        post_instance = db.get(key)

        # Storing values from the user
        self.title = cgi.escape(self.request.get('title'))
        self.post = cgi.escape(self.request.get('post'))

        # Updating the post instance values
        post_instance.title = str(self.title)
        post_instance.post = str(self.post)
        post_instance.put()

        self.redirect('/%s' % str(post_instance.key().id()))


class DeletePost(Handler):
    def get(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)

        # Finds and stores the post instance by id from the database
        post_instance = db.get(key)

        # If post instance exists then check if logged in username matches with
        # post saved author, if does - delete the post
        if self.user:
            if post_instance:
                if self.user.username == post_instance.author:
                    post_instance.delete()
                self.redirect('/')
        else:
            self.redirect('/login')



class EditComment(Handler):
    def get(self, comment_id):
        # Pulls the id of the comment from the link
        key = self.get_comment_key(comment_id)

        # Finds and stores the comment instance by id from the database
        comment_instance = db.get(key)

        # If user exists and logged in user's username equals to comment's
        # author username render edit comment

        if self.user:
            if self.user.username == comment_instance.author:
                self.render('editcomment.html', comment=comment_instance)
        else:
            self.redirect('/%s' % str(comment_instance.post_id))

    def post(self, comment_id):
        # Pulls the id of the comment from the link
        key = self.get_comment_key(comment_id)

        # Finds and stores the comment instance by id from the database
        comment_instance = db.get(key)

        # Storing values from the user
        self.comment = self.request.get('comment')

        # If user exists and logged in user's username equals to comment's
        # author username update comment values in db
        if self.user.username == comment_instance.author:
            comment_instance.body = str(self.comment)
            comment_instance.put()

        self.redirect('/%s' % str(comment_instance.post_id))


class DeleteComment(Handler):
    def get(self, comment_id):
        key = self.get_comment_key(comment_id)

        # Finds and stores the comment instance by id from the database
        comment_instance = db.get(key)

        # If user exists and logged in user's username equals to comment's
        # author username delete comment
        if self.user:
            if self.user.username == comment_instance.author:
                comment_instance.delete()

        self.redirect('/%s' % str(comment_instance.post_id))


class SinglePost(Handler):
    def get(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)

        # Finds and stores the post instance by id from the database
        post = db.get(key)

        # Get all posts matching the post_id and order them by date descending
        comments = Comment.all().filter('post_id =', int(post_id))
        likes = Like.all().filter('post_id =', int(post_id))

        # Default value for users that are not logged in
        username_status = False

        # If user is logged in then set the default value to be currently
        # logged in user's username
        if self.user:
            username_status = self.user.username

        # Pull the Like from the database that matches currently logged in
        # user's username and post id

        user_like = Like.all().filter('author =', username_status).filter(
            'post_id =', int(post_id))

        # If post not found throws a 404 error
        if not post:
            self.error(404)
            return

        # Renders the single post
        self.render("singlepost.html", post=post, comments=comments,
                    likes=likes, user_like=user_like)

    def post(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)
        # Finds and stores the post instance by id from the database
        post_instance = db.get(key)

        self.body = cgi.escape(self.request.get('comment'))

        if self.user and self.body:
            # Finds and stores the post instance by id from the database
            # and then updates it
            comment = Comment.add_comment(self.body, self.user.username,
                                          int(post_id))
            comment.put()

        self.redirect('/%s' % str(post_instance.key().id()))


class LikePost(Handler):
    def get(self, post_id):
        # Pulls the id of the post from the link
        key = self.get_post_key(post_id)
        # Finds and stores the post instance by id from the database
        post_instance = db.get(key)

        # If user exists pull all the likes by the user in the post (by post id)
        if self.user:
            likes = Like.all().filter('author =', self.user.username).filter(
                'post_id =', int(post_id))

            # If post instance author does not equal to the currently
            # logged in user's username
            if not post_instance.author == self.user.username:

                #If total amount of records in DB equals 0, add the new record
                if likes.count() == 0:
                    add_like = Like.add_like(True, self.user.username,
                                             int(post_id))
                    add_like.put()

                # Else remove the record
                else:
                    likes.get().delete()

            self.redirect('/%s' % str(post_instance.key().id()))
        else:
            self.redirect('/login')

class Signup(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        # Storing default value for error, if error is detected change to true
        has_error = False

        # Storing values from the user
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        # Displaying proper error if user input is invalid
        if not valid_username(self.username):
            params['error_username'] = "Username is invalid."
            has_error = True

        if not valid_password(self.password):
            params['error_password'] = "Password is invalid."
            has_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords do not match."
            has_error = True

        if not valid_email(self.email):
            params['error_email'] = "Email is invalid."
            has_error = True

        if has_error:
            self.render('signup.html', **params)

        # If no errors detected, check for username in database - if does not exist create a new one.
        else:
            self.done()

    def done(self):
        return NotImplementedError


class Register(Signup):
    def done(self):

        # Search for username inputted by user, store instance of user
        # object inside a variable
        u = User.by_name(self.username)

        # If username matches the one inside db then show an error
        if u:
            error_form = 'User already exists, please log in'
            self.render('signup.html', error_form=error_form)
        # Else create a new instance of User object
        else:
            u = User.register(self.username, self.password, self.email)

            # Send the user object into db
            u.put()

            # Set the hashed cookie of username and redirect user to "/"
            self.set_secure_cookie('username', self.username)
            self.redirect('/')


class Login(Handler):
    def get(self):
        self.render('login.html')

    def post(self):
        self.username = self.request.get('username')
        self.password = self.request.get('password')

        # Find the user matching the user's input in the database
        u = User.all().filter('username =', self.username).get()

        # If user has been found set the hashed cookie and render homepage
        if u and check_valid_pw(self.username, self.password, u.password):
            self.set_secure_cookie('username', self.username)
            self.redirect('/')

        # Else render login page and display error
        else:
            error_form = 'Incorrect username or password'
            self.render('login.html', error_form=error_form)


class Logout(Handler):
    def get(self):
        # Set the username cookie to be empty and redirect to signup page
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')
        self.redirect('/signup')


app = webapp2.WSGIApplication(
    [('/?', Homepage),
     ('/signup', Register),
     ('/login', Login),
     ('/logout', Logout),
     ('/addpost', AddPost),
     ('/editpost/([0-9]+)', EditPost),
     ('/deletepost/([0-9]+)', DeletePost),
     ('/editcomment/([0-9]+)', EditComment),
     ('/deletecomment/([0-9]+)', DeleteComment),
     ('/likepost/([0-9]+)', LikePost),
     ('/([0-9]+)', SinglePost)
     ],
    debug=True)
