from main import *

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
