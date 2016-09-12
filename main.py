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
import os
import jinja2
import webapp2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class MainHandler(Handler):
    def render_bloghome(self, subject="", content="", error="", posts=""):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("bloghome.html", subject=subject, content = content, error=error, posts=posts)

    def get(self):
        self.render_bloghome()

class BlogHandler(Handler):
    def get(self):
        self.render("bloghome.html")

class NewPostHandler(Handler):
    def render_blogpost(self, subject="", content="", error="", posts=""):
        posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 5")
        self.render("blogpost.html", subject=subject, content = content, error=error, posts=posts)

    def get(self):
        self.render_blogpost()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = BlogPost(subject=subject, content = content) #create art object from the database class
            a.put() #store entity in the database
            id = a.key().id()
            self.redirect("/blog/"+ str(id))
        else:
            error = "we need a subject and content!"
            self.render_blogpost(subject, content, error)

class ViewPostHandler(Handler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id))

        if not post:
            self.render("permalink.html", post = post, error = "This blog entry does NOT exist")
        else:
            self.render("permalink.html", post = post)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog', BlogHandler),
    ('/newpost', NewPostHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
