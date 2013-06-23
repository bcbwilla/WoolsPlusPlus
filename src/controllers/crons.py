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
import time
import logging
import random
import urllib
import json

from google.appengine.ext import db
from google.appengine.api import urlfetch_errors
from google.appengine.api import memcache
from google.appengine.api import runtime
import pAProfileScraper as pap
import numpy

from models.models import Player, Graph, Commit, RecentStats, ServerStats, Histogram
from config import config
import pageh
from plot import Plot


players_to_update = []

class UpdateStatsHandler(webapp2.RequestHandler):
    """Updates all player's stats"""


    
    def get(self):
        
        q = Player().all()
        if q != None:
            q = list(q)
 
            k = 0
            while k < len(q) and not runtime.is_shutting_down():
                player = q[k]
                
                url = config.base_url + str(player.name)
                # get stats
                try:
                    p_stats = pap.PAProfileScraper(url, kills=True, deaths=True, objectives=True)
                except (urlfetch_errors.DeadlineExceededError, IndexError):
                    continue
                
                if p_stats == None:
                    continue

                p = self.__update_player_stats(player, p_stats)

                # update recent stats
                RecentStats.get_or_insert(p.name,name=p.name,date=p.dates[-1],kills=p.kills[-1],
                                          deaths=p.deaths[-1],cores=p.cores[-1],wools=p.wools[-1],
                                          monuments=p.monuments[-1],objectives=p.objectives[-1],
                                          kd=p.kd[-1],cd=p.cd[-1],wd=p.wd[-1],md=p.md[-1],od=p.od[-1],
                                          rkd7=p.rkd7[-1],rcd7=p.rcd7[-1],rwd7=p.rwd7[-1],
                                          rmd7=p.rmd7[-1],rod7=p.rod7[-1],rk7=p.rk7[-1],rd7=p.rd7[-1],
                                          rc7=p.rc7[-1],rw7=p.rw7[-1],rm7=p.rm7[-1],ro7=p.ro7[-1])
                
                if runtime.is_shutting_down():
                    logging.info('backend runtime is shutting down.')
            
                k = k + 1

            self.__server_stats(players_to_update)
            
            db.put(players_to_update)
            
            # flush memcache
            flushed = memcache.flush_all()
            if flushed:
                logging.info('memecache flushed')
            else:
                logging.error('unable to flush memcache')


    def __update_player_stats(self, player, p_stats):
        # update everyone's stats first
            
            # explicitly compute KD so we have it with more decimal places
            if p_stats.deaths != 0:  
                kd = float(p_stats.kills)/p_stats.deaths
            else:
                kd = float(p_stats.kills)
            

            # regular stats
            #fields to update
            stats = ['kills', 'deaths', 'cores', 'wools', 'monuments', 'objectives',
                     'cd', 'wd', 'md', 'od']
            
            for stat in stats:
                value = getattr(p_stats, stat)
                values = getattr(player, stat)
                values.append(value)
                setattr(player, stat, values)
                
                
            # do kd seperately for better precision
            value = kd
            values = getattr(player, 'kd')
            values.append(value)
            setattr(player, 'kd', values)    
            
            value = datetime.now()
            values = getattr(player, 'dates')
            values.append(value)
            setattr(player, 'dates', values)                
                                    

            # rolling stats
            roll_index = self.__get_rolling(config.n_days, player.dates)
            # updated rolling stat/deaths
            player = self.__update_rolling_stats(player, roll_index, div_deaths=True)
            # update rolling regular stats
            player = self.__update_rolling_stats(player, roll_index, div_deaths=False)
            
            players_to_update.append(player)

            return player
    
    def __update_rolling_stats(self, player, roll_index, div_deaths=True):  
        """updates a player's rolling stats
        
        num_days:   number of days used in computing rolling stat
        div_deaths: true if you are computing a rolling stat that involves
                    dividing by deaths (e.g. kd)
        
        """ 
          
        if div_deaths:      
            # rolling stat/deaths.
            stats_to_compute = [('kills', 'kd'), ('cores', 'cd'), ('wools', 'wd'), 
                                ('monuments', 'md'), ('objectives', 'od')] 
        else:
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
            setattr(player, rs_name, values)
        return player
          
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

    def __server_stats(self, players):

        kills = []
        deaths = []
        cores = []
        wools = []
        monuments = []
        kd = []

        for p in players:
            kills.append(p.kills[-1])
            deaths.append(p.deaths[-1])
            cores.append(p.cores[-1])
            wools.append(p.wools[-1])
            monuments.append(p.monuments[-1])
            kd.append(p.kd[-1])

        kills = numpy.array(kills)
        deaths = numpy.array(deaths)
        cores = numpy.array(cores)
        wools = numpy.array(wools)
        monuments = numpy.array(monuments)
        kd = numpy.array(kd)

        total_kills = int(kills.sum())
        total_deaths = int(deaths.sum())
        total_cores = int(cores.sum())
        total_wools = int(wools.sum())
        total_monuments = int(monuments.sum())

        avg_kills = float(kills.mean())
        avg_deaths = float(deaths.mean())
        avg_cores = float(cores.mean())
        avg_wools = float(wools.mean())
        avg_monuments = float(monuments.mean())
        avg_kd = float(kd.mean())

        std_kills = float(kills.std())
        std_deaths = float(deaths.std())
        std_cores = float(cores.std())
        std_wools = float(wools.std())
        std_monuments = float(monuments.std())
        std_kd = float(kd.std())


        ServerStats(total_kills=total_kills,total_deaths=total_deaths,total_cores=total_cores,
                   total_wools=total_wools,total_monuments=total_monuments,
                   avg_kills=avg_kills,avg_deaths=avg_deaths,avg_cores=avg_cores,
                   avg_wools=avg_wools,avg_monuments=avg_monuments,avg_kd=avg_kd,
                   std_kills=std_kills,std_deaths=std_deaths,std_cores=std_cores,
                   std_wools=std_wools,std_monuments=std_monuments,std_kd=std_kd).put()    

        def make_hist(stat_ary, bins=10, std=False):
            """make histogram and convert from numpy 
               float 64 arrays to lists of regular floats
               
                stat_ary MUST be a numpy array """

            if not std:
                h_range = (min(stat_ary) - 1, max(stat_ary) + 1)
            else:
                m = stat_ary.mean()
                std_d = stat_ary.std()
                h_range = (m-std_d*float(std), m+std_d*float(std))



            y,x = numpy.histogram(stat_ary,bins=bins,range=h_range,density=True)
            y,x = y.tolist(),x.tolist()
            # convert all elements to float because GAE doesn't like numpy floats.
            x = [ float(xi) for xi in x ]
            y = [ float(yi) for yi in y ]
            return x,y

        num_bins = kd.size // 2

        # make histograms - all data
        x,y = make_hist(kd, bins=num_bins)
        Histogram(name='kd',x=x,y=y).put()

        x,y = make_hist(kills, bins=num_bins)
        Histogram(name='kills',x=x,y=y).put()

        x,y = make_hist(deaths, bins=num_bins)
        Histogram(name='deaths',x=x,y=y).put()

        x,y = make_hist(wools, bins=num_bins)
        Histogram(name='wools',x=x,y=y).put()

        x,y = make_hist(cores, bins=num_bins)
        Histogram(name='cores',x=x,y=y).put()

        x,y = make_hist(monuments, bins=num_bins)
        Histogram(name='monuments',x=x,y=y).put()

        # make histograms - only include data 1 std from mean
        x,y = make_hist(kd, bins=num_bins, std=1)
        Histogram(name='kd_1std',x=x,y=y).put()

        x,y = make_hist(kills, bins=num_bins, std=1)
        Histogram(name='kills_1std',x=x,y=y).put()

        x,y = make_hist(deaths, bins=num_bins, std=1)
        Histogram(name='deaths_1std',x=x,y=y).put()

        x,y = make_hist(wools, bins=num_bins, std=1)
        Histogram(name='wools_1std',x=x,y=y).put()

        x,y = make_hist(cores, bins=num_bins, std=1)
        Histogram(name='cores_1std',x=x,y=y).put()

        x,y = make_hist(monuments, bins=num_bins, std=1)
        Histogram(name='monuments_1std',x=x,y=y).put()
        

class UpdatePlotsHandler(webapp2.RequestHandler):
    """Updates all player's plots"""

    def get(self):        
        q = Player().all()
        if q != None:
            q = list(q)

            # only update 20 random player's graphs to conserve resources
            random.shuffle(q)
            if len(q) > 20:
                q = q[:20]
                        
            # now update everyone's graphs. done separately so a problem with a player's 
            # plots don't stop the rest of the players' stats from being updated.
            k = 0
            while k < len(q) and not runtime.is_shutting_down():             
                player = q[k] 
                # Make some graphs
                pplot = Plot(player, stats=[('kd','KD')])
                pplot.plot_regular()
                Graph.get_or_insert(pplot.filename, user=pplot.player.name, 
                                    filename=pplot.filename, image=pplot.data)
 
                pplot = Plot(player, stats=[('rw7','RW7'),('rc7', 'RC7'),('rm7','RM7')])
                pplot.plot_regular()
                Graph.get_or_insert(pplot.filename, user=pplot.player.name, 
                                    filename=pplot.filename, image=pplot.data)
 
                # plot fancy graph
                pplot = Plot(player)
                pplot.plot_rk7rd7rkd7()
                Graph.get_or_insert(pplot.filename, user=pplot.player.name, 
                                    filename=pplot.filename, image=pplot.data)
               
                if runtime.is_shutting_down():
                    logging.info('backend runtime is shutting down.')                
                 
                k = k + 1
             
            # flush memcache
            flushed = memcache.flush_all()
            if flushed:
                logging.info('memecache flushed')
            else:
                logging.error('unable to flush memcache')

class UpdateCommits(webapp2.RequestHandler):
    
    def get(self):
        COMMIT_URL = 'https://api.github.com/repos/bcbwilla/WoolsPlusPlus/commits?per_page=1000'
        try:
            page = urllib.urlopen(COMMIT_URL)
        except:
            return
        
        html = page.read()
        page.close()
        commits = json.loads(html)
        
        for commit in commits:
            sha = commit['sha']
            url = commit['html_url']
            message = commit['commit']['message']
            d = commit['commit']['committer']['date']
            d = self.format_commit_date(d)
            committer_name = commit['author']['login']
            committer_url = commit['author']['html_url']
            Commit.get_or_insert(sha, url=url, message=message, date=d,
                                 committer_name=committer_name, committer_url=committer_url)

    def format_commit_date(self, d):
        # python magic.  BAM!
        d = time.strptime(" ".join(d.split('T'))[:-1],"%Y-%m-%d %H:%M:%S")
        return datetime(d.tm_year, d.tm_mon, d.tm_mday, d.tm_hour, d.tm_min,d. tm_sec)

        

