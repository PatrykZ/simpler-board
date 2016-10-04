from main import *

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
