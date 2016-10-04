from main import *

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

        # If post instance exists then check if logged in username matches with
        # post saved author, if does - edit the post
        if self.user:
            if self.user.username == post_instance.author:
                # Storing values from the user
                self.title = cgi.escape(self.request.get('title'))
                self.post = cgi.escape(self.request.get('post'))

                # Updating the post instance values
                post_instance.title = str(self.title)
                post_instance.post = str(self.post)
                post_instance.put()

        self.redirect('/%s' % str(post_instance.key().id()))
