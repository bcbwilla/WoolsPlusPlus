import datetime
from google.appengine.ext import db

class Graph(db.Model):
    user = db.StringProperty(default=None)  
    filename = db.StringProperty(default=None)
    image = db.BlobProperty(default=None)
    
class Player(db.Model):
    name = db.StringProperty()
    rolling = db.IntegerProperty()
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
    rkd = db.ListProperty(float, default=None)
    rcd = db.ListProperty(float, default=None)
    rwd = db.ListProperty(float, default=None)
    rmd = db.ListProperty(float, default=None)
    rod = db.ListProperty(float, default=None)
    