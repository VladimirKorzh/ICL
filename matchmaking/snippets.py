from itertools import izip_longest
from urllib import quote
import re

import ValveApiWrapper
from matchmaking.models import Hero, Player

# neat snippet for coupling of elements
def grouper(iterable, n, fillvalue=None):
    # Collect data into fixed-length chunks or blocks
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)
    
def escape_username(username):
    # escapes weird characters in player username and returns quoted string
    # it produces %D0%AF%D0%99%D0%9A%D0%90 string which can be read by mubmle url protocol                
    # checked that is works for as weird nicknames as Rus(K,F)!@#$%^&*()as
    escape = re.compile(ur'[^\w]',re.UNICODE)
    result = escape.sub('', unicode(username))
    return quote ( result.encode('utf8') )  
                           
def refresh_hero_list():
    # Perform a full reload of heroes table
    # Should be used on new DB and in case of newly released heroes
    vapi = ValveApiWrapper.ValveApi()
    hero_list = vapi.get_hero_list()
    
    for each in Hero.objects.all():
        each.delete()
    
    for each in hero_list:
        hero = Hero()
        hero.name = each
        hero.save()    

def get_session_info(request):
    # saving some space, these lines are too repetitive
    data = {}
    if request.user.is_authenticated():
        data['social_auth'] = request.user.social_auth.get(provider='steam')
        data['steamid']     = data['social_auth'].extra_data.get('steamid')     
        data['personaname'] = data['social_auth'].extra_data.get('personaname')
        
        try: 
            data['profile'] = Player.objects.get(uid=data['steamid'])
        except Player.DoesNotExist:
            pass
    return data
        


  
  
  
#def get_time_elapsed(player):
      #time_since_last_seen = datetime.utcnow() - player.last_updated.replace(tzinfo=None)
      #splits = str(time_since_last_seen).split(':')
      #pretty_time = ''
      
      #if splits[0] != '0':
        #pretty_time += splits[0] + ' hours '
        
      #if splits[1] != '0':
        #pretty_time += splits[1] + ' minutes ago.'

      #return pretty_time            