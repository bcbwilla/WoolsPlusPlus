"""
Set all the url handlers to the corresponding urls
"""

import webapp2
import logging

from controllers import crons, imageh
from controllers import pageh

logging.getLogger().setLevel(logging.INFO)
app = webapp2.WSGIApplication([('/', pageh.MainPage), 
                               ('/crons/updatestats', crons.UpdateStatsHandler),
                               (r'/users/(.*)', pageh.ProfileHandler),
                               ('/image', imageh.ImageHandler),
                               ('/allusers',pageh.AllUsersHandler),
                               ('/about',pageh.AboutHandler),
                               ('/login',pageh.LoginHandler)
                               ], debug=True)

