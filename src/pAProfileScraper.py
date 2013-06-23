'''
Created on Mar 24, 2013

@author: Ben
'''

from bs4 import BeautifulSoup
from google.appengine.api import urlfetch
from google.appengine.api import urlfetch_errors

class PAProfileScraper:
    """Fetch available profile information from Project Ares profile page
    
    url -- full url of the profile to scrape
       
    """
    
    def __init__(self, url, all_stats=False, kills=False, deaths=False, friends=False, kk=False, 
                 kd=False, server_joins=False, forum_posts=False, topics_started=False, 
                 objectives=False, punishments=False, badges=False):
        
        self.url = url     
        self.soup = self.make_soup(url)
        if self.soup == None:
            return None
        
        try:
            if self.check_user():
                if kills or deaths or friends or all_stats:
                    self.fetch_kills_section()
                if kd or kk or server_joins or forum_posts or topics_started or all_stats:
                    self.fetch_kd_section()
                if objectives or all_stats:
                    self.fetch_objectives()
                if punishments or all_stats:
                    self.fetch_punishments()
                if badges or all_stats:
                    self.fetch_badges()
            else:
                return "Player doesn't exist!"
        except IndexError:
            print "Index out of range error for player with url " + url
        
    def check_user(self):
        page_title = self.soup.find('title').contents[0]
        #see if use exists! if they don't, the page gives a 404
        if "404" in page_title:
            return False
        else:
            return True
          
    def make_soup(self, url):
        #a make a da soup-a  
        try:
            stuffs = urlfetch.fetch(url,validate_certificate=False, deadline=300)
        except urlfetch_errors.DeadlineExceededError:
            return None
        html = stuffs.content
        return BeautifulSoup(html)
    
    def fetch_kills_section(self):
            #get kills-deaths section
        kills_deaths_friends = self.soup.findAll('div', {"class" : "span2"})      
        self.kills = int(kills_deaths_friends[0].h2.contents[0])
        self.deaths = int(kills_deaths_friends[1].h2.contents[0])
        self.friends = str(kills_deaths_friends[2].h2.contents[0])
        
    def fetch_kd_section(self): 
        #get kk-kd section
        kdkk_table = self.soup.findAll('div', {"class" : "span3"})[1].findAll('h2')  
        self.kd = float(kdkk_table[0].contents[0])
        self.kk = float(kdkk_table[1].contents[0])
        self.server_joins = int(kdkk_table[2].contents[0])
        self.forum_posts = int(kdkk_table[3].contents[0])
        self.topics_started = int(kdkk_table[4].contents[0])
        
    def fetch_objectives(self):
        #get objectives section
        table = self.soup.findAll('div', {"class" : "span4"})
        objs_table = []
        for i in range(len(table)):
            if table[i].h2 != None:
                objs_table.append(table[i].h2.contents[0])
        if len(objs_table) >= 2:             
            self.wools = int(objs_table[0])
            self.cores = int(objs_table[1])
            self.monuments = int(objs_table[2])
            self.objectives = self.wools + self.cores + self.monuments
        else:
            self.wools = None
            self.cores = None
            self.monuments = None
            self.objectives = None  
                 
        if self.deaths != 0:
            self.wd = float(self.wools)/self.deaths
            self.cd = float(self.cores)/self.deaths
            self.md = float(self.monuments)/self.deaths
            self.od = float(self.objectives)/self.deaths
        else:
            self.wd = None
            self.cd = None
            self.md = None
            self.od = None
        
    def fetch_punishments(self):
        #punishments
        table =self.soup.findAll('table', {"class" : "table table-bordered table-striped"})
        self.punishments = len(table[0].tbody.findAll("tr"))
       
    def fetch_badges(self): 
        #badges
        table = self.soup.findAll("div", style='width: 168px; text-align: center;')
        if len(table) > 0:
            badge_section = table[0].findAll("span", {"class" : "label"})
            badges = []
            for badge in badge_section:
                badges.append(badge.contents[0].string)
            self.badges = badges
        else:
            self.badges = None
        
            