import webapp2
import jinja2
import os

from google.appengine.ext import db

from models.models import Player


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))

class AboutHandler(webapp2.RequestHandler):
    
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render())