"""
renders a player's profile page
"""

import webapp2
import jinja2
import os
from datetime import datetime

from google.appengine.ext import db

from models.models import Player


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))

class ProfileHandler(webapp2.RequestHandler):
    
    def get(self, player_name):       
        player_name = player_name.lower()
        player = Player.get_by_key_name(player_name)
        
        if player:            
            base_img_url = '/image?filename='+player_name+'_'
            # images to display
            img_urls = [base_img_url+'rkd7kd',
                        base_img_url+'kd', 
                        base_img_url+'wdcdmd']
            
            # stats to print in stats table
            print_list = ['time','kills','deaths','kd','wd','cd','md','od','rkd7']
            table_size = len(player.kills)
            stat_length = len(player.kills)
            # convert time to relative time
            date_strings = build_rel_times(player)
                   
            template_values = {
                'player': player,
                'img_urls': img_urls,
                'print_list': print_list,
                'table_size': table_size,
                'stat_length': stat_length,
                'date_strings': date_strings
            }
    
            template = JINJA_ENVIRONMENT.get_template('profile.html')
            self.response.write(template.render(template_values))
            
        else:
            self.error(404)
            
            
def build_rel_times(player):
    date_strings=[]
    for date in player.dates:
        date_strings.append(convert_time(date))
    return date_strings

def convert_time(date):
    now = datetime.now() 
    td = now - date 
    days, hours, minutes, seconds = td.days, td.seconds // 3600, td.seconds // 60 % 60, td.seconds

    if days >= 1:
        if days == 1:
            return str(days) + " day ago"
        else:
            return str(days) + " days ago"
    elif hours < 24 and hours >= 1:
        if hours == 1:
            return str(hours) + " hour ago"
        else:
            return str(hours) + " hours ago"
    elif minutes < 60 and minutes >= 1:
        if minutes == 1:
            return str(minutes) + " minute ago"
        else:
            return str(minutes) + " minutes ago"
    elif seconds < 60:
        if seconds == 1:
            return str(seconds) + " second ago"
        else:
            return str(seconds) + " seconds ago"
    else:
        return None