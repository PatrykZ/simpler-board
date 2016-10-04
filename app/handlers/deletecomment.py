from main import *

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
