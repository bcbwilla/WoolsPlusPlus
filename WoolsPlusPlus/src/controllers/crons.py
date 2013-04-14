import webapp2
import datetime

from google.appengine.ext import db
import pAProfileScraper as pap

from models.models import Player
from config import config
#from plot import Plot


class UpdateStatsHandler(webapp2.RequestHandler):
    
    def get(self):        
        q = Player().all()
        if q != None:
            for player in q:
                url = config.base_url + str(player.name)
                p_stats = pap.PAProfileScraper(url, kills=True, deaths=True, objectives=True)
                
                if p_stats.deaths != 0:
                    kd = float(p_stats.kills)/p_stats.deaths
                else:
                    kd = float(p_stats.kills)
                
                #fields to update
                stats = ['kills', 'deaths', 'cores', 'wools', 'monuments', 'objectives',
                         'cd', 'wd', 'md', 'od']
                for stat in stats:
                    update_player_value(player, stat, getattr(p_stats, stat))
                
                #do KD separately from explicit calculation to get me decimal places
                update_player_value(player, 'kd', kd)
                update_player_value(player, 'dates', datetime.datetime.now())
                update_rolling_stats(player)
                
                
                
                # Make some graphs
#                pplot = Plot(player, stats=[('kd','KD'),('rkd', 'RKD ('+str(player.rolling)+' days)')])
#                pplot.put()
#                pplot = Plot(player, stats=[('rod','ROD ('+str(player.rolling)+' days)')])
#                pplot.put()
#                pplot = Plot(player, stats=[('wd','WD'),('cd', "CD"),('md','MD')])
#                pplot.put()
#                pplot = Plot(player, stats=[('kd','KD')])
#                pplot.put()


@db.transactional
def update_player_value(player, stat, value):
    values = getattr(player, stat)
    # see if the user has filled the data list
    values.append(value)
    if len(values) > config.max_entries:
        i = len(values) - config.max_entries
        values = values[i:]
    setattr(player, stat, values)
    player.put()


@db.transactional
def update_rolling_stats(player):    
    stats_to_compute = [('kills', 'kd'), ('cores', 'cd'), ('wools', 'wd'), 
             ('monuments', 'md'), ('objectives', 'od')] 
    for stat in stats_to_compute:
        # get normal stat list
        stats = getattr(player, stat[0])

        # get index for start date of rolling stat
        rolling = get_rolling(config.n_days, player.dates)
        player.rolling = rolling[1]
        # get rolling value for that stat 
        rs = rolling_stat(stats, player.deaths, rolling[0])
        # add rolling value to rolling value list
        rs_name = 'r'+stat[1]
        values = getattr(player, rs_name)
        values.append(rs)
        if len(values) > config.max_entries:
            i = len(values) - config.max_entries
            values = values[i:] 
    
        setattr(player, rs_name, values)
        player.put()
        
def rolling_stat(stats, deaths, index):         
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
    
def get_rolling(days, dates):
    current = dates[-1]
    for i,v in enumerate(reversed(dates)):
        print i,v, (current - v).days
        if (current - v).days >= days:
            n = days
            i = len(dates) - i - 1
            return (i, n)
        else:
            ind = 0
            n = (current - dates[0]).days
    return (ind, n)

