from main import *

class Logout(Handler):
    def get(self):
        # Set the username cookie to be empty and redirect to signup page
        self.response.headers.add_header('Set-Cookie', 'username=; Path=/')
        self.redirect('/signup')
