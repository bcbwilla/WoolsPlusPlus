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
Set all the url handlers to the corresponding urls
"""

import webapp2
import logging

from controllers import crons, imageh
from controllers import pageh

logging.getLogger().setLevel(logging.INFO)
app = webapp2.WSGIApplication([('/', pageh.MainPage), 
                               ('/crons/updatestats', crons.UpdateStatsHandler),
                               ('/crons/updateplots', crons.UpdatePlotsHandler),
                               ('/crons/updatecommits', crons.UpdateCommits),
                               (r'/users/(.*)', pageh.ProfileHandler),
                               ('/image', imageh.ImageHandler),
                               ('/allusers',pageh.AllUsersHandler),
                               ('/about',pageh.AboutHandler),
                               ('/login',pageh.LoginHandler),
                               ('/revisions',pageh.RevisionsHandler)
                               ], debug=True)

