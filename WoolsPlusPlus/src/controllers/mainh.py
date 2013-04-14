import webapp2
import cgi
import jinja2
import os

from google.appengine.api import urlfetch

from models.models import Player
from config import config

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))
        
class MainPage(webapp2.RequestHandler):
    
    def render_page(self, msg="", p_url="", url_msg=""):
        template_values = {
            'msg': msg,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
    
    def get(self):       
#        initialize_players()        
        self.render_page()

    def post(self):
        player_name = cgi.escape(self.request.get('content'))

        if player_name == '':
            self.render_page() 
        else:
            if confirm_player(player_name):
                p_url = "/users/" + player_name
                add_player(player_name)
                self.redirect(p_url)       
            else:
                self.render_page(msg="Player doesn't exist, you dirty trickster.")



def confirm_player(player_name):
    url = config.base_url + player_name
    result = urlfetch.fetch(url, validate_certificate=False)
    if result.status_code == 200:
        return True
           
def add_player(player_name):
    player_name = player_name.lower()
    p = Player()
    if not p.get_by_key_name(player_name):
        p.get_or_insert(player_name, name=player_name)
        return True
    else:
        return False
           
def initialize_players():
    #create initial player object. for debugging only
    player_list = ["bcbwilla", "ieatboulders2", "HxRxK", "wadeflash03"]
    
    for p_name in player_list:
        p_name = p_name.lower()  
        Player().get_or_insert(p_name, name=p_name)