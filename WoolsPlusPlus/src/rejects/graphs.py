import webapp2
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.api import files
from google.appengine.api import images

from plot import make_plot
from models import player


class PlotHandler(webapp2.RequestHandler):
    def get(self):
#        self.response.headers['Content-Type'] = 'image/png'

        q = player.Player.all()
        q.filter("name = ","bcbwilla")
        p = q.get()
        
        plot_image = make_plot(p, stat='kd', title='Test', xlabel='fuckyeah')
        self.write_blob(plot_image, "bcbwilla", "bcbwilla_graph.png")
        
        self.response.out.write(self.get_userFile("bcbwilla"))
        
        
    def write_blob(self, data, user, file_name):
        blob = files.blobstore.create(_blobinfo_uploaded_filename=file_name)
        with files.open(blob, 'a') as f:
            f.write(data)
        files.finalize(blob)
    
        # Add a userfile entry for this blob
        key =  files.blobstore.get_blob_key(blob)
        userFile = UserFile(blob_key = key, user = user) 
        userFile.put()
        
    def get_userFile(self, user):
        userfiles = db.GqlQuery("SELECT * "
                                "FROM UserFile "
                                "WHERE user = :1",user)
    
    #    for userfile in userfiles:
    #        filename = userfile.blob_key.filename
    #    filename = userfiles[0].blob_key.filename    
        key = userfiles[0].blob_key
        s_url = images.get_serving_url(key)
        return s_url
        
class UserFile(db.Model):
    user = db.StringProperty(required=True)  
    filename = db.StringProperty()
    blob_key = blobstore.BlobReferenceProperty(required=True)
    
