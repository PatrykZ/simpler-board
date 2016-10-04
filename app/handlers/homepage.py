from main import *

class Homepage(Handler):
    def get(self):
        # Gets all the posts from the database and sorts them
        # from newest to oldest date of submission
        posts = Post.all().order('-date')

        # Renders the homepage along with all the posts
        self.render('homepage.html', posts=posts)
