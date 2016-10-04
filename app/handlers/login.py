from main import *

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
