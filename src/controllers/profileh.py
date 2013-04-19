"""
renders a player's profile page
"""

import webapp2
import jinja2
import os

from google.appengine.ext import db

from models.models import Player


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))

class ProfileHandler(webapp2.RequestHandler):
    
    def get(self, player_name):       
        player_name = player_name.lower()
        player = Player.get_by_key_name(player_name)
        
        if player:            
            sz_in_mb = len(db.model_to_protobuf(player).Encode())*9.53674*(10**(-7))
            
            base_img_url = '/image?filename='+player_name+'_'
            # images to display
            img_urls = [base_img_url+'kdrkd',
                        base_img_url+'rod', 
                        base_img_url+'wdcdmd']
            
            # stats to print in stats table
            print_list = ['date','kills','deaths','kd','wd','cd','md','od']
            table_size = len(player.kills)
            stat_length = len(player.kills)
                   
            template_values = {
                'player': player,
                'size': sz_in_mb,
                'img_urls': img_urls,
                'print_list': print_list,
                'table_size': table_size,
                'stat_length': stat_length
            }
    
            template = JINJA_ENVIRONMENT.get_template('profile.html')
            self.response.write(template.render(template_values))
            
        else:
            self.error(404)