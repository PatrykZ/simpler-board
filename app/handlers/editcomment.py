from main import *

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
        self.comment = cgi.escape(self.request.get('comment'))

        # If user exists and logged in user's username equals to comment's
        # author username update comment values in db
        if self.user.username == comment_instance.author:
            comment_instance.body = str(self.comment)
            comment_instance.put()

        self.redirect('/%s' % str(comment_instance.post_id))
