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
produces plots
"""

import cStringIO
import logging

from google.appengine.ext import db
#import matplotlib.pyplot as plt
#import matplotlib as mpl
#from pylab import ScalarFormatter

from models.models import Graph

logging.getLogger().setLevel(logging.INFO)

class Plot:
    def __init__(self, player, stats=[('kd','KD')], ylabel='', title='', rolling=0):
        self.player = player
        self.filename = player.name+'_'
        self.dates = player.dates
        self.stats = stats
        self.ylabel = ylabel
        self.title = title
        
    def plot_regular(self):
        dates = mpl.dates.date2num(self.dates)    
        fig = plt.figure()
        fig.set_size_inches(6,3)
        ax = fig.add_subplot(111, axisbg='white')
        
        # for some reason plot_date is not auto generating new colors for each new function 
        l_c = ['b', 'g', 'r', 'c', 'm', 'y']
        i = 0

        for stat in self.stats:
            # for plot line colors
            if i >= len(l_c):
                i = 0
            stat_list = getattr(self.player, stat[0])
            
            # get first occurrence that isn't "-1"
            ri = [j for j,x in enumerate(stat_list) if x != -1]
            if len(ri) >= 1:
                r = ri[0] # index of first good data
            else: # there's no data to plot
                self.data = None
                return None
  
            plt.plot_date(dates[r:], stat_list[r:], ls='-', linewidth=2, 
                          label=stat[1], color=l_c[i],ms=0)
            i+=1
            self.filename+=stat[0]
        
        
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(10)
            
        fig.autofmt_xdate()           
        ax.legend(loc=2, prop={'size':9})
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False)) 
        plt.ylabel(self.ylabel)
        
        if self.title == '':
            title="wools++ (alpha)  player: " + self.player.name
            plt.title(title, fontsize=11)
        else:
            plt.title(self.title)
        
        sio = cStringIO.StringIO()
        plt.savefig(sio, format="png", dpi=100, transparent=True)
        self.data = sio.getvalue()

    def plot_rk7rd7rkd7(self):
        rk7 = self.player.rk7
        rd7 = self.player.rd7
        rkd7 = self.player.rkd7        
        dates = mpl.dates.date2num(self.dates) 
        
        # get first occurrence that isn't "-1"
        ri = [j for j,x in enumerate(rk7) if x != -1]
        if len(ri) >= 1:
            r = ri[0] # index of first good data
        else: # there's no data to plot
            self.data = None
            return None
                 
        fig = plt.figure()
        fig.set_size_inches(6,3)
        ax1 = fig.add_subplot(111) 
        
        ax1.plot_date(dates[r:], rk7[r:], ls='--', linewidth=2, color='c',ms=0)
        ax1.plot_date(dates[r:], rd7[r:], ls='--', linewidth=2, color='m',ms=0)
        
        fig.autofmt_xdate()
        #two axes
        ax2 = ax1.twinx()
        ax2.plot_date(dates[r:], rkd7[r:], ls='-', color='y',ms=0)
        
        ax1.legend(['RK7','RD7'], loc=3, prop={'size':9})
        ax2.legend(['RKD7'], loc=4, prop={'size':9})
        for tick in ax1.xaxis.get_major_ticks():
            tick.label.set_fontsize(10) 
             
        plt.gca().yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        
        if self.title == '':
            title="wools++ (alpha)  player: " + self.player.name
            plt.title(title, fontsize=11)
        else:
            plt.title(self.title)
        
        sio = cStringIO.StringIO()
        plt.savefig(sio, format="png", dpi=100, transparent=True)
        self.data = sio.getvalue()
        self.filename+='rk7rd7rkd7'
