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
handles image requests
"""

import webapp2
import logging

from google.appengine.ext import db
from google.appengine.api import memcache

class ImageHandler(webapp2.RequestHandler):
    def get(self):
        filename = self.request.get('filename')
        image = get_image(filename)
        if (image and image.image):
            self.response.headers['Content-Type'] = 'image/png'
            self.response.out.write(image.image)


def get_image(filename):
    result = memcache.get(filename)
    if result is not None and len(result) > 0:
        logging.info('got '+filename+' from the memcache')
        return result[0]
    else:
        result = db.GqlQuery("SELECT * FROM Graph WHERE filename = :1 LIMIT 1",
                    filename).fetch(1)
        memcache.add(filename, result, 60)
        logging.info('added '+filename+' to the memcache')
        if (len(result) > 0):
            return result[0]
        else:
            return None
    