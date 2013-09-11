
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player


from urllib import quote
import re

import mm

import ValveApiWrapper


def landing(request):
  if not request.user.is_authenticated():
      return redirect('/intro')
  else:
      # fix for people reloading page after update has been released.
      return login(request)

def intro(request):
  data = {}
  if request.user.is_authenticated():
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')     
    data['profile'] = Player.objects.get(uid=steamid) 
  
  return render(request, 'intro.html', data)  

  
def help(request, topic):
  data = {}
  if request.user.is_authenticated():
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')     
    data['profile'] = Player.objects.get(uid=steamid) 
    
  filename = str(topic) + '.html'
  return render(request, filename, data)
  
  
  
def escape_username(nickname):
    # escapes weird characters in player username and returns quoted string
    # it produces %D0%AF%D0%99%D0%9A%D0%90 string which can be read by mubmle url protocol                
    # checked that is works for as weird nicknames as Rus(K,F)!@#$%^&*()as
    escape = re.compile(ur'[^\w]',re.UNICODE)
    result = escape.sub('', unicode(nickname))
    return quote ( result.encode('utf8') )  
  
  
@login_required  
def login(request):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')
    personaname = social_auth.extra_data.get('personaname')

    try:
      player = Player.objects.get(uid=steamid)
    except Player.DoesNotExist:
      player = Player()
      
    player.uid      = steamid
    player.nickname = personaname
    player.avatar   = social_auth.extra_data.get('avatar')
    player.mumble_nickname = escape_username(personaname)

    player.save()
    print "Player logged in:", player.nickname
    print "Mumble nickname:", player.mumble_nickname
    
    return redirect('/stacks')
 
 
 
@login_required
def profile(request, profile_id):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')  
    
    data = {'pl': Player.objects.get(id__exact=profile_id),
	    'profile': Player.objects.get(uid=steamid)
	    }
    
    print data['profile'].nickname,' is looking at profile ', data['pl'].nickname
    
    return render(request,'profile_modal.html', data)
      
 
@login_required
def refresh(request):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')    

    player_obj = Player.objects.get(uid=steamid)
      
    if request.method != 'POST':        
      valveapi    = ValveApiWrapper.ValveApi()        
      playerstats = valveapi.get_player_exp_from_steamid(steamid)    
      player_obj.exp             = playerstats['exp']
      player_obj.nickname        = playerstats['nickname']
      player_obj.exp_n_games     = playerstats['exp_n_games']
      player_obj.exp_h_games     = playerstats['exp_h_games']
      player_obj.exp_vh_games    = playerstats['exp_vh_games']
      player_obj.exp_total_games = playerstats['total_games']
      player_obj.extra_exp_pts   = playerstats['extra_exp_pts']    
      print 'Refreshing stats for player', player_obj.nickname
    
    if request.method == 'POST':
      print 'Setting new player roles', request.POST['pri_role'], request.POST['alt_role'], 'for player', player_obj.nickname
      player_obj.pri_role = request.POST['pri_role']
      player_obj.alt_role = request.POST['alt_role']
    
    player_obj.save()
    
    return redirect('/stacks') 
    
    
    

