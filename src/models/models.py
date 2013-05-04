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

"""
datastore models
"""

from datetime import datetime
from google.appengine.ext import db

class Account(db.Model):
    """Represents a user's account"""
    nickname = db.StringProperty(default=None)  
    mc_account = db.StringProperty(default=None)
    profile_url = db.StringProperty(default=None)

class Graph(db.Model):
    """Represents a player's graph"""
    user = db.StringProperty(default=None)  
    filename = db.StringProperty(default=None)
    image = db.BlobProperty(default=None)
    
    
class Player(db.Model):
    """Represents a player"""
    name = db.StringProperty()
    dates = db.ListProperty(datetime)
    kills = db.ListProperty(int, default=None)
    deaths = db.ListProperty(int, default=None)
    cores = db.ListProperty(int, default=None)
    wools = db.ListProperty(int, default=None)
    monuments = db.ListProperty(int, default=None)
    objectives = db.ListProperty(int, default=None)
    kd = db.ListProperty(float, default=None)
    cd = db.ListProperty(float, default=None)
    wd = db.ListProperty(float, default=None)
    md = db.ListProperty(float, default=None)
    od = db.ListProperty(float, default=None)
    rkd7 = db.ListProperty(float, default=None)
    rcd7 = db.ListProperty(float, default=None)
    rwd7 = db.ListProperty(float, default=None)
    rmd7 = db.ListProperty(float, default=None)
    rod7 = db.ListProperty(float, default=None)
    rk7 = db.ListProperty(int, default=None)
    rd7 = db.ListProperty(int, default=None)
    rc7 = db.ListProperty(int, default=None)
    rw7 = db.ListProperty(int, default=None)
    rm7 = db.ListProperty(int, default=None)
    ro7 = db.ListProperty(int, default=None)   