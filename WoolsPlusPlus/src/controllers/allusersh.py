import webapp2
import jinja2
import os

from google.appengine.ext import db

from models.models import Player


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))

class AllUsersHandler(webapp2.RequestHandler):
    
    def get(self):
        player_list = Player.all()
        player_list.order("name")
               
        template_values = {
            'player_list': player_list,
        }

        template = JINJA_ENVIRONMENT.get_template('allusers.html')
        self.response.write(template.render(template_values))