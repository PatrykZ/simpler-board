from main import *
from app.utils.validator import *

class Signup(Handler):
    def get(self):
        self.render('signup.html')

    def post(self):
        # Storing default value for error, if error is detected change to true
        has_error = False

        # Storing values from the user
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        # Displaying proper error if user input is invalid
        if not valid_username(self.username):
            params['error_username'] = "Username is invalid."
            has_error = True

        if not valid_password(self.password):
            params['error_password'] = "Password is invalid."
            has_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords do not match."
            has_error = True

        if not valid_email(self.email):
            params['error_email'] = "Email is invalid."
            has_error = True

        if has_error:
            self.render('signup.html', **params)

        # If no errors detected, check for username in database - if does not exist create a new one.
        else:
            self.done()

    def done(self):
        return NotImplementedError


class Register(Signup):
    def done(self):

        # Search for username inputted by user, store instance of user
        # object inside a variable
        u = User.by_name(self.username)

        # If username matches the one inside db then show an error
        if u:
            error_form = 'User already exists, please log in'
            self.render('signup.html', error_form=error_form)
        # Else create a new instance of User object
        else:
            u = User.register(self.username, self.password, self.email)

            # Send the user object into db
            u.put()

            # Set the hashed cookie of username and redirect user to "/"
            self.set_secure_cookie('username', self.username)
            self.redirect('/')
