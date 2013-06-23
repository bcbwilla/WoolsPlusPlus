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
    dates = db.ListProperty(datetime, default=None)
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

class RecentStats(db.Model):
    """Represents a player's most recent stats"""
    name = db.StringProperty()
    date = db.DateTimeProperty(auto_now=True)
    kills = db.IntegerProperty()
    deaths = db.IntegerProperty()
    cores = db.IntegerProperty()
    wools = db.IntegerProperty()
    monuments = db.IntegerProperty()
    objectives = db.IntegerProperty()
    kd = db.FloatProperty()
    cd = db.FloatProperty()
    wd = db.FloatProperty()
    md = db.FloatProperty()
    od = db.FloatProperty()
    rkd7 = db.FloatProperty()
    rcd7 = db.FloatProperty()
    rwd7 = db.FloatProperty()
    rmd7 = db.FloatProperty()
    rod7 = db.FloatProperty()
    rk7 = db.IntegerProperty()
    rd7 = db.IntegerProperty()
    rc7 = db.IntegerProperty()
    rw7 = db.IntegerProperty()
    rm7 = db.IntegerProperty()
    ro7 = db.IntegerProperty()
    
class Commit(db.Model):
    """Represents a commit"""
    url = db.LinkProperty()
    message = db.StringProperty(multiline=True)
    date = db.DateTimeProperty()
    date_string = db.StringProperty()
    committer_name = db.StringProperty()
    committer_url = db.LinkProperty()

class ServerStats(db.Model):
    """Represents a server wide stat"""
    date = db.DateTimeProperty(auto_now_add=True)
    total_kills = db.IntegerProperty()
    total_deaths = db.IntegerProperty()
    total_cores = db.IntegerProperty()
    total_wools = db.IntegerProperty()
    total_monuments = db.IntegerProperty()
    avg_kills = db.FloatProperty()
    avg_deaths = db.FloatProperty()
    avg_cores = db.FloatProperty()
    avg_wools = db.FloatProperty()
    avg_monuments = db.FloatProperty()
    avg_kd = db.FloatProperty()
    std_kills = db.FloatProperty()
    std_deaths = db.FloatProperty()
    std_cores = db.FloatProperty()
    std_wools = db.FloatProperty()
    std_monuments = db.FloatProperty()
    std_kd = db.FloatProperty()



class Histogram(db.Model):
    """Represents a stat histogram"""
    date = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty(required=True)
    x = db.ListProperty(float)
    y = db.ListProperty(float)
