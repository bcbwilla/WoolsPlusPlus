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

from models.models import Player, Account
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
        player_list = Player.all()  # get all the players to display
        player_list.order("name")
        player_list = list(player_list)
        
        account = get_user_account()
        if account is not None:
            user=True
        else:
            user=False
            
        self.render_page(player_list, account=account, user=user)
    
    def render_page(self, player_list, account=None, user=False):     
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Users',
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url,
            'player_list': player_list
        }
        template = JINJA_ENVIRONMENT.get_template('allusers.html')
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
    
    
class ProfileHandler(webapp2.RequestHandler):
    """ render player profile """
    
    def get(self, player_name):       
        player_name = player_name.lower()
        
        player = self.get_player(player_name)
        
        if player:
            # images
            base_img_filename = player_name+'_'
            # images to display
            img_urls = [base_img_filename+'kd', 
                        base_img_filename+'rw7rc7rm7',
                        base_img_filename+'rk7rd7rkd7']
            # see what images to display
            graph_urls = []
            for img_filename in img_urls:
                if imageh.get_image(img_filename) != None:
                    graph_urls.append("/image?filename="+img_filename)

            stat_length = len(player.kills)
            if stat_length >= 1:
                stat_table_size = 15  #maximum size for stats table
                p_stats = self.prepare_player_data(player, stat_table_size)
                stat_table_size = len(p_stats['kills'])  #updated size for stats table if p doesn't have enough
                r_stat_table_size = len(p_stats['kd'])
            else:
                stat_table_size = 0
                stat_table_size = 0
                p_stats = None
                r_stat_table_size = 0
                     
            account = get_user_account()
            if account is not None:
                user=True
            else:
                user=False
                
            self.render_page(player, stat_length, stat_table_size, r_stat_table_size,
                              graph_urls, config.n_entries, account=account, user=user, p_stats=p_stats)
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
            
    def prepare_player_data(self, player, stat_table_size):
        
        def recent_data(l, stat_table_size, r=False):
            if r: # if rolling stat
                i = l[::-1].index(-1) # find last occurance of -1
                l = l[i+1:]  #trim off all "-1" entries so we don't print those
                
            l_reversed = list(reversed(l))
            l_length = len(l)
            if l_length < stat_table_size:
                return l_reversed[:l_length+1]
            else:
                return l_reversed[:stat_table_size+1]

        stat_types = ['kills','deaths','cores','wools','monuments','objectives',
                      'kd','wd','cd','md','od']
        r_stat_types = ['rkd7','rcd7','rwd7','rmd7','rod7',
                       'rk7','rd7','rc7','rw7','rm7','ro7']
        
        stat_dict = {}
        for stat in stat_types:
            stat_dict[stat] = recent_data(getattr(player,stat), stat_table_size)
        
        for r_stat in r_stat_types:
            stat_dict[r_stat] = recent_data(getattr(player,r_stat), stat_table_size, r=True)
                     
        stat_dict['dates'] = recent_data(build_rel_times(player), stat_table_size)
        
        return stat_dict
        
        
    def render_page(self, player, stat_length, stat_table_size, r_stat_table_size,
                     graph_urls, n_entries, p_stats=None, account=None, user=False):       
        if account is not None:
            user_profile_url = account.profile_url
        else:
            user_profile_url = None
        
        template_values = {
            'page_title': 'Profile',
            'player': player,
            'graph_urls': graph_urls,
            'stat_table_size': stat_table_size,
            'r_stat_table_size': r_stat_table_size,
            'stat_length': stat_length,
            'n_entries': n_entries,
            'logout_url': users.create_logout_url('/'),
            'user': user,
            'user_profile_url': user_profile_url
        }
        
        # add stats stuff
        if p_stats is not None:
            template_values.update(p_stats)
        
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
#                self.render_page(msg="You've already linked an account!", render_form=False, account=account,
#                                 user=True)
        else:
            self.redirect(users.create_login_url(self.request.uri))

    def post(self):
        mc_account = cgi.escape(self.request.get('content')).strip()
             
        if mc_account == '':
            self.render_page() 
        else:
            if confirm_player(mc_account):
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
                        self.render_page(msg="Successfully linked.", error=False, p_url=p_url)                     
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
 
    
#class RegisterHandler(webapp2.RequestHandler):
#    """ renders registration page """
#    
#    def get(self):
#        user = users.get_current_user()
#        if user:
#            account = Account.get_by_key_name(str(user.nickname))
#            if account is None:
#                self.render_page()
#            else:
#                self.render_page(msg="You've already linked an account!", render_form=False, account=account,
#                                 user=True)
#        else:
#            self.redirect(users.create_login_url(self.request.uri))
#
#    def post(self):
#        mc_account = cgi.escape(self.request.get('content')).strip()
#             
#        if mc_account == '':
#            self.render_page() 
#        else:
#            if confirm_player(mc_account):
#                user = users.get_current_user()
#                if user:
#                    # update account
#                    account = Account.get_by_key_name(str(user.nickname))
#                    if account is not None:
#                        self.render_page(msg="You've already linked an account!", render_form=False)
#                    else:
#                        p_url = "/users/" + mc_account
#                        add_account(mc_account, str(user.nickname), p_url)
#                        # add user
#                        add_player(mc_account)
#                        self.render_page(msg="Successfully linked.", error=False, p_url=p_url)                     
#                else:
#                    self.redirect(users.create_login_url(self.request.uri))                  
#            else:
#                self.render_page(msg="Player doesn't exist, you dirty trickster.", error=True)
#
#    def render_page(self, account=None, user=False, msg="", p_url="", error=False, render_form=True):
#        if account is not None:
#            user_profile_url = account.profile_url
#        else:
#            user_profile_url = None
#        
#        template_values = {
#            'page_title': 'Register',
#            'msg': msg,
#            'error': error,
#            'p_url': p_url,
#            'render_form': render_form,
#            'logout_url': users.create_logout_url('/'),
#            'user': user,
#            'user_profile_url': user_profile_url
#        }
#        template = JINJA_ENVIRONMENT.get_template('register.html')
#        self.response.write(template.render(template_values))


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