"""
produces plots
"""

import cStringIO

from google.appengine.ext import db
import matplotlib.pyplot as plt
import matplotlib as mpl
from pylab import ScalarFormatter

from models.models import Graph


class Plot:
    def __init__(self, player, stats, ylabel='', title='', rolling=0):
        self.player = player
        self.filename = player.name+'_'
        self.dates = player.dates
        self.stats = stats
        self.ylabel = ylabel
        self.title = title
#        self.rolling = rolling
        
    def plot_regular(self):
        dates = mpl.dates.date2num(self.dates)    
        fig = plt.figure()
        fig.set_size_inches(6,3)
        ax = fig.add_subplot(111, axisbg='white')
        
        # for some reason plot_date is not auto generating new colors for each new function 
        l_c = ['b', 'g', 'r', 'c', 'm', 'y']
        i = 0
#        r = self.rolling # if a rolling plot, skip the first r entries since they are nonsense.

        for stat in self.stats:
            # for plot line colors
            if i >= len(l_c):
                i = 0
            stat_list = getattr(self.player, stat[0])
            
            # get first occurance that isn't "-1"
            ri = [i for i,x in enumerate(stat_list) if x != -1]
            if len(ri) >= 1:
                r = ri[0] # index of first good data
            else: # there's no data to plot
                self.data = None
                return None
  
            
            plt.plot_date(dates[r:], stat_list[r:], ls='-', linewidth=2, label=stat[1], color=l_c[i])
            i+=1
            self.filename+=stat[0]
        
        
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(10)
            
        fig.autofmt_xdate()           
        ax.legend(loc=2, prop={'size':9})
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False)) 
        plt.ylabel(self.ylabel)
        
        if self.title == '':
            title="wools++ (alpha)  Player: " + self.player.name
            plt.title(title, fontsize=11)
        else:
            plt.title(self.title)
        
        sio = cStringIO.StringIO()
        plt.savefig(sio, format="png", dpi=100, transparent=True)
        self.data = sio.getvalue()


    def put(self):
        """adds or updates a user's graph"""
        user = self.player.name
        filename = self.filename
        image = self.data
        if image:
            g = Graph().get_by_key_name(filename)
            # see if graph exists
            if g is None:
                Graph().get_or_insert(filename,user=user, filename=filename, image=image)
            else:
                self.__update_graph(g, image)


    @db.transactional
    def __update_graph(self, graph, image):
        """updates a user's graph"""
        graph.image = image
        graph.put()
