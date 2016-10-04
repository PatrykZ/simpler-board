from main import *

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
