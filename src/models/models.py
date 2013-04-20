"""
datastore models
"""

import datetime
from google.appengine.ext import db


class Graph(db.Model):
    """Represents a player's graph"""
    user = db.StringProperty(default=None)  
    filename = db.StringProperty(default=None)
    image = db.BlobProperty(default=None)
    
    
class Player(db.Model):
    """Represents a player"""
    name = db.StringProperty()
    dates = db.ListProperty(datetime.datetime)
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
    