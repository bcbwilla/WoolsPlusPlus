from google.appengine.ext import db
from google.appengine.ext import blobstore

class UserFile(db.Model):
    user = db.StringProperty(required=True)  
    filename = db.StringProperty()
    graph = db.BlobProperty(default=None)