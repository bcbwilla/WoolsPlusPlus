"""
produces plots
"""

import cStringIO

from google.appengine.ext import db
import matplotlib.pyplot as plt
import matplotlib as mpl

from models.models import Graph


class Plot:
    def __init__(self, player, stats, ylabel='', title='', rolling=14):
        self.player = player
        p = self.player
        self.filename = p.name+'_'
        
        dates = mpl.dates.date2num(p.dates)    
        fig = plt.figure()
        fig.set_size_inches(6,3)
        ax = fig.add_subplot(111) 

        
        # for some reason plot_date is not auto generating new colors for each new function 
        l_c = ['b', 'g', 'r', 'c', 'm', 'y']
        i = 0
        for stat in stats:
            if i >= len(l_c):
                i = 0
            stat_list = getattr(p, stat[0])
            plt.plot_date(dates, stat_list, ls='-', linewidth=2, label=stat[1], color=l_c[i])
            i+=1
            self.filename+=stat[0]
            
        ax.legend(loc=2, prop={'size':9})
        fig.autofmt_xdate()   
        plt.ylabel(ylabel)
        if title == '':
            title="wools++ (alpha)  Player: " + p.name
            plt.title(title, fontsize=11)
        else:
            plt.title(title)
        
        sio = cStringIO.StringIO()
        plt.savefig(sio, format="png", dpi=100)
        self.data = sio.getvalue()


    def put(self):
        """adds or updates a user's graph"""
        user = self.player.name
        filename = self.filename
        image = self.data
        g = Graph().get_by_key_name(filename)
        # see if graph exists
        if g is None:
            Graph().get_or_insert(filename,user=user, filename=filename, image=image)
        else:
            update_graph(g, image)

        
@db.transactional
def update_graph(graph, image):
    """updates a user's graph"""
    graph.image = image
    graph.put()