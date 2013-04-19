"""
Set all the url handlers to the corresponding urls
"""

import webapp2

from controllers import crons, profileh, mainh, imageh, allusersh, abouth, updateschema


app = webapp2.WSGIApplication([('/', mainh.MainPage), 
                               ('/crons/updatestats', crons.UpdateStatsHandler),
                               (r'/users/(.*)', profileh.ProfileHandler),
                               ('/image', imageh.ImageHandler),
                               ('/allusers',allusersh.AllUsersHandler),
                               ('/about',abouth.AboutHandler),
                               ('/updateschema',updateschema.UpdateSchema)
                               ], debug=True)
