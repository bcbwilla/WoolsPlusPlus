#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


'''
This is a one-time job to restructure the player object in the data store.
Updating to a new rolling value definition, and removing current ones.
'''

import webapp2

from google.appengine.ext import db

from models.models import Player


class UpdateSchema(webapp2.RequestHandler):
    """Updates all player's stats and makes data plots"""
    
    def get(self):        
        q = Player().all()
        q.filter("name =","bcbwilla")
        p = q.get()
        if p != None:
            for attr, value in p.__dict__.iteritems():
                if len(value) > 13:
                    delete_player_val(p, attr, value)
                    
#        if q != None:
#            for player in q:
#                stats_to_update = ['rk7','rd7','rc7','rw7','rm7','ro7']
#                for stat in stats_to_update:
#                    l = len(player.kills)
#                    new_stat = [-1]*l
#                    update_player_value(player, stat, new_stat)
#                
#                stats_to_update = ['rkd7', 'rcd7', 'rwd7', 'rmd7', 'rod7']
#                for stat in stats_to_update:
#                    l = len(player.kills)
#                    new_stat = [-1.0]*l
#                    update_player_value(player, stat, new_stat)
#                
#                stats_to_delete = ['rkd','rcd', 'rwd', 'rmd', 'rod', 'rolling']
#                for stat in stats_to_delete:
#                    delete_player_value(player, stat)

#
#@db.transactional
#def update_player_value(player, stat, value):
#    """updates a player's value""" 
#    setattr(player, stat, value)
#    player.put()
#    
#@db.transactional
#def delete_player_value(player, stat):
#    """updates a player's value""" 
#    delattr(player, stat)
#    player.put()              
#    
@db.transactional
def delete_player_val(player, stat, value):
    """updates a player's value""" 
    value = value[:-1]
    setattr(player, stat, value)
    player.put()         