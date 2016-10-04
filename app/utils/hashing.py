import random
import hmac
import hashlib
from string import letters


# Secret value for hashing
secret = 'd22j192dj12jd912jds8912dj8'



# Function that generates a hash based on the secret value and returns it
# in a format of value | hash
def hash_item(s):
    return '%s|%s' % (s, hmac.new(secret, s).hexdigest())


# Function that checks if the value that is being passed is correct, by
# comparing it against the make_secure_val() function
def check_hash_item(hash):
    val = hash.split('|')[0]
    if hash == hash_item(val):
        return val


# Function that creates a random string of 5 letters
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


# Function that creates a password hash
def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s, %s' % (salt, h)


# Function that checks the hashed password
def check_valid_pw(name, pw, h):
    val = h.split(',')[0]
    if h == make_pw_hash(name, pw, val):
        return h
