"""
contains the cron job that collects data from oc.tc
"""

import webapp2
import datetime

from google.appengine.ext import db
import pAProfileScraper as pap

from models.models import Player
from config import config
from plot import Plot


class UpdateStatsHandler(webapp2.RequestHandler):
    """Updates all player's stats and makes data plots"""
    
    def get(self):        
        q = Player().all()
        if q != None:
            for player in q:
                url = config.base_url + str(player.name)
                # get stats
                p_stats = pap.PAProfileScraper(url, kills=True, deaths=True, objectives=True)
                
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
                self.__update_player_value(player, 'dates', datetime.datetime.now())
                self.__update_rolling_stats(player)
                             
                # Make some graphs
                pplot = Plot(player, stats=[('kd','KD'),('rkd', 'RKD ('+str(player.rolling)+' days)')])
                pplot.put()
                pplot = Plot(player, stats=[('rod','ROD ('+str(player.rolling)+' days)')])
                pplot.put()
                pplot = Plot(player, stats=[('wd','WD'),('cd', "CD"),('md','MD')])
                pplot.put()


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
    def __update_rolling_stats(self, player):  
        """updates a player's rolling stats""" 
         
        stats_to_compute = [('kills', 'kd'), ('cores', 'cd'), ('wools', 'wd'), 
                 ('monuments', 'md'), ('objectives', 'od')] 
        for stat in stats_to_compute:
            # get normal stat list
            stats = getattr(player, stat[0])
    
            # get index for start date of rolling stat
            rolling = self.__get_rolling(config.n_days, player.dates)
            player.rolling = rolling[1]
            # get rolling value for that stat 
            rs = self.__rolling_stat(stats, player.deaths, rolling[0])
            # add rolling value to rolling value list
            rs_name = 'r'+stat[1]
            values = getattr(player, rs_name)
            values.append(rs)
            if len(values) > config.max_entries:
                i = len(values) - config.max_entries
                values = values[i:] 
        
            setattr(player, rs_name, values)
            player.put()
    
          
    def __rolling_stat(self, stats, deaths, index):   
        """computes a player's rolling stat"""
              
        last_s = stats[-1]
        first_s = stats[index]
        last_d = deaths[-1]
        first_d = deaths[index]
        
        if last_s != None and first_s != None and last_d != None and first_d != None:
            delta_s = float(last_s-first_s)   
            delta_d = last_d - first_d
        else:
            return None
        
        if delta_d != 0:
            return delta_s/delta_d
        else:
            return delta_s
    
    
    def __get_rolling(self, days, dates):
        """returns the number of stats to use to achieve a rolling interval of a given length
        
        days is specified in the config file, and is the number of days to include in a rolling
        interval.
        """
        
        current = dates[-1]
        for i,v in enumerate(reversed(dates)):
            if (current - v).days >= days:
                n = days
                i = len(dates) - i - 1
                return (i, n)
            else:
                ind = 0
                n = (current - dates[0]).days
        return (ind, n)