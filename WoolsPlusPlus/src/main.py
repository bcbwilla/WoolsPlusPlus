#from google.appengine.ext import webapp2
import webapp2
from controllers import crons, profileh, mainh, imageh, allusersh, abouth

app = webapp2.WSGIApplication([('/', mainh.MainPage), 
                               ('/crons/updatestats', crons.UpdateStatsHandler),
                               (r'/users/(.*)', profileh.ProfileHandler),
                               ('/image', imageh.ImageHandler),
                               ('/allusers',allusersh.AllUsersHandler),
                               ('/about',abouth.AboutHandler)
                               ], debug=True)
