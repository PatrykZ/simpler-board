from main import *

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
