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
contains the cron job that collects data from oc.tc
"""

import webapp2
from datetime import datetime
import logging

from google.appengine.ext import db
from google.appengine.api import urlfetch_errors
from google.appengine.api import memcache
import pAProfileScraper as pap

from models.models import Player
from config import config
#from plot import Plot


class UpdateStatsHandler(webapp2.RequestHandler):
    """Updates all player's stats and makes data plots"""
    
    def get(self):        
        q = Player().all()
        if q != None:
            q = list(q)
            # update everyone's stats first
            for player in q:
                url = config.base_url + str(player.name)
                # get stats
                try:
                    p_stats = pap.PAProfileScraper(url, kills=True, deaths=True, objectives=True)
                except (urlfetch_errors.DeadlineExceededError, IndexError):
                    continue
                
                if p_stats == None:
                    continue
                
                # explicitly compute KD so we have it with more decimal places
                if p_stats.deaths != 0:  
                    kd = float(p_stats.kills)/p_stats.deaths
                else:
                    kd = float(p_stats.kills)
                
                #fields to update
                stats = ['kills', 'deaths', 'cores', 'wools', 'monuments', 'objectives',
                         'cd', 'wd', 'md', 'od']
                
                for stat in stats:
                    self.__update_player_value(player, stat, getattr(p_stats, stat))
                # update KD separately from explicit calculation to get more decimal places
                self.__update_player_value(player, 'kd', kd)
                self.__update_player_value(player, 'dates', datetime.now())
                # get index for start date of rolling stat
                roll_index = self.__get_rolling(config.n_days, player.dates)
                # updated rolling stat/deaths
                self.__update_rolling_stats(player, roll_index, div_deaths=True)
                # update rolling regular stats
                self.__update_rolling_stats(player, roll_index, div_deaths=False)
            
            # now update everyone's graphs. done separately so a problem with a player's 
            # plots don't stop the rest of the players' stats from being updated.
#            for player in q:               
#                # Make some graphs
#                pplot = Plot(player, stats=[('kd','KD')])
#                pplot.plot_regular()
#                pplot.put()
#                pplot = Plot(player, stats=[('rw7','RW7'),('rc7', "RC7"),('rm7','RM7')])
#                pplot.plot_regular()
#                pplot.put()
#                pplot = Plot(player, stats=[('rw7','RW7'),('rc7','RC7'),('rm7','RM7')])
#                pplot.plot_regular()
#                pplot.put()
#                # plot fancy graph
#                pplot = Plot(player)
#                pplot.plot_rk7rd7rkd7()
#                pplot.put()
#            
            # flush memcache
            flushed = memcache.flush_all()
            if flushed:
                logging.info('memecache flushed')
            else:
                logging.error('unable to flush memcache')


    @db.transactional
    def __update_player_value(self, player, stat, value):
        """updates a player's value"""
        
        values = getattr(player, stat)
        values.append(value)
        # see if the user has filled the data list
        if len(values) > config.max_entries:
            i = len(values) - config.max_entries
            values = values[i:]
        setattr(player, stat, values)
        player.put()
    
    
    @db.transactional
    def __update_rolling_stats(self, player, roll_index, div_deaths=True):  
        """updates a player's rolling stats
        
        num_days:   number of days used in computing rolling stat
        div_deaths: true if you are computing a rolling stat that involves
                    dividing by deaths (e.g. kd)
        
        """ 
          
        if div_deaths:
            logging.info('Start rolling stat/death for '+player.name)          
            # rolling stat/deaths.
            stats_to_compute = [('kills', 'kd'), ('cores', 'cd'), ('wools', 'wd'), 
                     ('monuments', 'md'), ('objectives', 'od')] 
        else:
            logging.info('Start regular rolling stat for '+player.name)
            # rolling stat
            stats_to_compute = [('kills', 'k'), ('deaths', 'd'), ('cores', 'c'), ('wools', 'w'), 
         ('monuments', 'm'), ('objectives', 'o')] 
            
        for stat in stats_to_compute:
            # get normal stat list
            stats = getattr(player, stat[0])
            # get rolling value for that stat 
            rs = self.__rolling_stat(stats, player.deaths, roll_index, div_deaths)
            # if user does not have data going to beginning of rolling interval
            if rs == None:
                # data in lists with stat/deaths are floats.
                # data in other stat lists are integers.  data store is strict like that.
                if div_deaths:              
                    rs = -1.0
                else:
                    rs = -1
                    
            
            # add rolling value to rolling value list
            rs_name = 'r'+stat[1]+str(config.n_days)
            values = getattr(player, rs_name)

            values.append(rs)
            # make sure data list isn't full. if it is, trim off the oldest values to
            # reduce it to correct length.
            if len(values) > config.max_entries:
                i = len(values) - config.max_entries
                values = values[i:] 
        
            setattr(player, rs_name, values)
            player.put()
        
    
          
    def __rolling_stat(self, stats, deaths, index, div_deaths):   
        """computes a player's rolling stat"""
        
        # make sure rolling stat does not extend to 
        # before when data started being collected
        if index:                          
            last_s = stats[-1]
            first_s = stats[index]
            last_d = deaths[-1]
            first_d = deaths[index]
            if last_s != None and first_s != None and last_d != None and first_d != None:
                delta_s = last_s - first_s   
                delta_d = last_d - first_d
            else:
                return None
            
            if delta_d != 0 and div_deaths:
                return float(delta_s)/float(delta_d)
            elif delta_d == 0 and div_deaths:
                return float(delta_s)
            elif div_deaths == False:
                return int(delta_s)
            
        else:
            return None
    
    
    def __get_rolling(self, days, dates):
        """returns the number of stats to use to achieve a rolling interval of a given length
        
        days is specified in the config file, and is the number of days to include in a rolling
        interval.
        """
        
        current = dates[-1]
        for i,v in enumerate(reversed(dates)):
            if (current - v).days >= days:
                index = len(dates) - i - 1
                return index
            else:
                index = None
        return index