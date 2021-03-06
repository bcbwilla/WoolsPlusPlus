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


""" handles the processing and displaying of all pages """

import webapp2, jinja2, os, cgi, logging
from datetime import datetime

from google.appengine.api import users, urlfetch, memcache

from models.models import Player, Account, Commit, RecentStats, Histogram, ServerStats
from controllers import imageh
from config import config


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), '../views')))


class AboutHandler(webapp2.RequestHandler):
    """ renders the 'about' page """
  
    def get(self):      
        account = get_user_account()
        if account is not None:
            self.render_page(account=account, user=True)
        else:
            self.render_page(user=False) 
    
    def render_page(self, account=None, user=False):      
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'About',
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url
        }
        template = JINJA_ENVIRONMENT.get_template('about.html')
        self.response.write(template.render(template_values))
           
        

class AllUsersHandler(webapp2.RequestHandler):
    """ renders the 'all users' page """

    def get(self):
#         player_list = memcache.get('player_list')
#         if player_list is not None:
#             logging.info('got player list from the memcache')
#         else:
#             player_list = Player.all()  # get all the players to display
#             player_list.order("name")
#             player_list = list(player_list)
#             if player_list is not None:
#                 memcache.add('player_list', player_list, 60)
#                 logging.info('added player_list to the memcache')
      
        page = self.request.get('page')
        sort = self.request.get('sort')
    
        if not sort:
            sort = 'kills'
        if not page or page < 1:
            page = 1
        page = int(page)

        PLAYERS_PER_PAGE = 20
        offset = (page-1)*PLAYERS_PER_PAGE

        q = RecentStats.all()  # get all the recent stats
        count = q.count() // PLAYERS_PER_PAGE + 1 # page count
        q.order('-'+str(sort))
        player_list = list(q.run(offset=offset,limit=PLAYERS_PER_PAGE))

        # convert join date to relative string
        for i in range(len(player_list)):
            p = player_list[i]
            if p.date:
                join_time = convert_time(p.date)
            else:
                join_time = "Today"

            p.date_str = join_time            
            player_list[i] =  p
        
        account = get_user_account()
        if account is not None:
            user=True
        else:
            user=False
            
        self.render_page(player_list, page, sort, count, PLAYERS_PER_PAGE, account=account, user=user)
    
    def render_page(self, player_list, page, sort, count, p_per_page, account=None, user=False):     
        if account is not None: 
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Users',
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url,
            'player_list': player_list,
            'page': page,
            'sort': sort,
            'count': count,
            'p_per_page': p_per_page,
            'base_url': '/allusers'
        }
        template = JINJA_ENVIRONMENT.get_template('allusers.html')
        self.response.write(template.render(template_values))
 
    
class RevisionsHandler(webapp2.RequestHandler):
    """ renders the 'revisions' page """

    def get(self):
        page = self.request.get('page')
        if not page or page < 1:
            page = 1
        page = int(page)

        REVISIONS_PER_PAGE = 10
        offset = (page-1)*REVISIONS_PER_PAGE

        account = get_user_account()
        if account is not None:
            user=True
        else:
            user=False
            
        q = Commit.all()  # get all the commites
        q.order("-date")
        count = q.count() // REVISIONS_PER_PAGE + 1 # page count
        commits_list = list(q.run(offset=offset,limit=REVISIONS_PER_PAGE))

        # convert commit date to relative date
        for i in range(len(commits_list)):
            commits_list[i].date_str = convert_time(commits_list[i].date)

        self.render_page(commits_list, page, count, account=account, user=user)
    
    def render_page(self, commits_list, page, count, account=None, user=False):     
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Revisions',
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url,
            'commits_list': commits_list,
            'page': page,
            'count': count,
            'base_url': '/revisions',
            'sort': 'date'
        }
        template = JINJA_ENVIRONMENT.get_template('revisions.html')
        self.response.write(template.render(template_values))
    
          
class MainPage(webapp2.RequestHandler):
    """ renders the main page """
    
    def get(self):        
        account = get_user_account()
        if account is not None:
            user = True
        else:
            user = False
                  
        self.render_page(account=account, user=user)
    
    def render_page(self, account=None, user=False, msg=""):       
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Home',
            'msg': msg,
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class StatsHandler(webapp2.RequestHandler):
    """ render player profile """
    
    def get(self):  
        page = self.request.get('page')    
        account = get_user_account()
        if account is not None:
            user=True
        else:
            user=False

        q = ServerStats.all() 
        q.order("-date")
        s = q.get()


        hists = {}

# TODO: put in fxn that also uses memcache
        q = Histogram.all()  
        q.filter("name =", "kd")
        q.order("-date")
        hists['kd_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "kills")
        q.order("-date")
        hists['kills_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "deaths")
        q.order("-date")
        hists['deaths_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "wools")
        q.order("-date")
        hists['wools_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "cores")
        q.order("-date")
        hists['cores_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "monuments")
        q.order("-date")
        hists['monuments_hist'] = q.get()


        q = Histogram.all()  
        q.filter("name =", "kd_1std")
        q.order("-date")
        hists['kd_1std_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "kills_1std")
        q.order("-date")
        hists['kills_1std_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "deaths_1std")
        q.order("-date")
        hists['deaths_1std_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "wools_1std")
        q.order("-date")
        hists['wools_1std_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "cores_1std")
        q.order("-date")
        hists['cores_1std_hist'] = q.get()

        q = Histogram.all()  
        q.filter("name =", "monuments_1std")
        q.order("-date")
        hists['monuments_1std_hist'] = q.get()
            
        self.render_page(page, s, hists, account=account, user=user)
              
        
    def render_page(self, page, stats, hists, account=None, user=False):       
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None

         
        template_values = {
            'page_title': 'Stats',
            's': stats,
            'page': page
        }
        template_values.update(hists)
        
        template = JINJA_ENVIRONMENT.get_template('stats.html')
        self.response.write(template.render(template_values))    


    
class ProfileHandler(webapp2.RequestHandler):
    """ render player profile """
    
    def get(self, player_name):      
        if player_name == '':
            self.redirect('/allusers')
        else:                   
            page = self.request.get('page')
            player_name = player_name.lower()
            player = self.get_player(player_name)
            
            if player:
                stat_length = len(player.kills)

                if stat_length >= 1:         
                    last_update_time = convert_time(player.dates[-1])
                else:
                    last_update_time = None 
                
                # get index of occurrence of rolling stat that isn't "-1"
                ri = [j for j,x in enumerate(player.rkd7) if x != -1]
                if len(ri) >= 1:
                    r_index = ri[0] # index of first good data
                else: # there's no data to plot
                    r_index = None
            
                account = get_user_account()
                if account is not None:
                    user=True
                else:
                    user=False
                    
                self.render_page(player, page, stat_length, r_index, last_update_time,
                                 account=account, user=user)
            else:
                self.redirect('/')
           
    def get_player(self, player_name):
        """gets player from memcache.  if not in memcache,
        player is added from database.
        """
        
        player = memcache.get(player_name)
        if player is not None:
            logging.info('got '+player.name+' from the memcache')
            return player
        else:
            player = Player.get_by_key_name(player_name)
            if player is not None:
                memcache.add(player_name, player, 60)
                logging.info('added '+player.name+' to the memcache')
                return player
            else:
                return
        
        
    def render_page(self, player, page, stat_length, r_index, last_update_time=None, 
                    account=None, user=False):       
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None

        
#
#   check that player.kd is not empty sequence!
#        min_y = min(player.kd) - 0.1
        min_y = 0
         
        template_values = {
            'page_title': 'Profile',
            'player': player,
            'page': page,
            'stat_length': stat_length,
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url,
            'last_update_time' : last_update_time,
            'r_index' : r_index,
            'min_y' : min_y
        }
        
        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values))
            
 
class LoginHandler(webapp2.RequestHandler):
    """ renders login page """
    
    def get(self):
       
        user = users.get_current_user()
        if user:
            account = Account.get_by_key_name(str(user.nickname))
            if account is None:
                self.render_page()
            else:
                self.redirect('users/'+str(account.mc_account))
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        mc_account = cgi.escape(self.request.get('content')).strip()
             
        if mc_account == '':
            self.render_page() 
        else:
            if confirm_player(mc_account):
                if get_account_assoc(mc_account):
                    self.render_page(msg=str(mc_account)+""" is already taken!  If you think this is a mistake,
                                    please contact me on the forums.""", error=True)            
                else:
                    user = users.get_current_user()
                    if user:
                        # update account
                        account = Account.get_by_key_name(str(user.nickname))
                        if account is not None:
                            self.render_page(msg="You've already linked an account!", render_form=False)
                        else:
                            p_url = "/users/" + mc_account
                            add_account(mc_account, str(user.nickname), p_url)
                            # add user
                            add_player(mc_account)
                            self.redirect('users/'+str(mc_account))                     
                    else:
                        self.redirect(users.create_login_url(self.request.uri))                  
            else:
                self.render_page(msg="Player doesn't exist, you dirty trickster.", error=True)

    def render_page(self, account=None, user=False, msg="", p_url="", error=False, render_form=True):
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Register',
            'msg': msg,
            'error': error,
            'p_url': p_url,
            'render_form': render_form,
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url
        }
        template = JINJA_ENVIRONMENT.get_template('register.html')
        self.response.write(template.render(template_values))


""" Some useful global functions """

def get_user_account():
    user = users.get_current_user()
    logging.info("getting user account")
    if user:
        account = Account.get_by_key_name(str(user.nickname))
        if account is not None:
            return account
        else:
            return
    else:
        return

def confirm_player(player_name):
    url = config.base_url + player_name
    result = urlfetch.fetch(url, validate_certificate=False)
    if result.status_code == 200:
        return True
           
def add_player(player_name):
    player_name = player_name.lower()
    p = Player()
    if not p.get_by_key_name(player_name):
        p.get_or_insert(player_name, name=player_name)
        return True
    else:
        return False
    
def add_account(mc_account, nickname, p_url):
    """updates an account"""
    Account().get_or_insert(nickname, mc_account=mc_account, 
                          nickname=nickname, profile_url=p_url)
    
def get_account_assoc(mc_account):
    """checks if mc account is already associated with an email"""
    q = Account.all()
    q.filter("mc_account =", mc_account)
    account = q.get()
    if account:
        return True # mc_account is already taken
    else:
        return False
    
def build_rel_times(player):
    """convert UTC time stamps to time elapsed since data collection"""
    
    date_strings=[]
    for date in player.dates:
        date_strings.append(convert_time(date))
    return date_strings

def convert_time(date):
    """converts past time stamp into relative time based on current time """
    
    now = datetime.now() 
    td = now - date 
    days, hours, minutes, seconds = td.days, td.seconds // 3600, td.seconds // 60 % 60, td.seconds

    if days >= 1:
        if days == 1:
            return str(days) + " day ago"
        else:
            return str(days) + " days ago"
    elif hours < 24 and hours >= 1:
        if hours == 1:
            return str(hours) + " hour ago"
        else:
            return str(hours) + " hours ago"
    elif minutes < 60 and minutes >= 1:
        if minutes == 1:
            return str(minutes) + " minute ago"
        else:
            return str(minutes) + " minutes ago"
    elif seconds < 60:
        if seconds == 1:
            return str(seconds) + " second ago"
        else:
            return str(seconds) + " seconds ago"
    else:
        return
