import webapp2

from google.appengine.ext import db

class ImageHandler(webapp2.RequestHandler):
    def get(self):
        filename = self.request.get('filename')
        image = getImage(filename)
        if (image and image.image):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(image.image)
        else:
            self.redirect('/static/noimage.png')

def getImage(filename):
    result = db.GqlQuery("SELECT * FROM Graph WHERE filename = :1 LIMIT 1",
                    filename).fetch(1)
    if (len(result) > 0):
        return result[0]
    else:
        return None