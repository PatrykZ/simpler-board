#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from app.handlers.homepage import *
from app.handlers.addpost import *
from app.handlers.editpost import *
from app.handlers.deletepost import *
from app.handlers.editcomment import *
from app.handlers.deletecomment import *
from app.handlers.singlepost import *
from app.handlers.likepost import *
from app.handlers.signup import *
from app.handlers.login import *
from app.handlers.logout import *


app = webapp2.WSGIApplication(
    [('/?', Homepage),
     ('/signup', Register),
     ('/login', Login),
     ('/logout', Logout),
     ('/addpost', AddPost),
     ('/editpost/([0-9]+)', EditPost),
     ('/deletepost/([0-9]+)', DeletePost),
     ('/editcomment/([0-9]+)', EditComment),
     ('/deletecomment/([0-9]+)', DeleteComment),
     ('/likepost/([0-9]+)', LikePost),
     ('/([0-9]+)', SinglePost)
     ],
    debug=True)
