from itertools import izip_longest
import re

import ValveApiWrapper

from matchmaking.models import Hero

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