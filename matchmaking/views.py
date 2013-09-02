
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player

from datetime import tzinfo, datetime
from urllib import quote

import mm
import MumbleWrapper
import ValveApiWrapper


def landing(request):
  if not request.user.is_authenticated():
      return redirect('/intro')
  else:
    # fix for people reloading page after update has been released.
      login(request)

def intro(request):
      return render(request, 'matchmaking/intro.html')  

@login_required  
def login(request):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')

    try:
      player = Player.objects.get(uid=steamid)
    except Player.DoesNotExist:
      player = Player()
      
    player.uid      = steamid
    player.nickname = str(request.user)
    player.avatar   = social_auth.extra_data.get('avatar')
    player.profile  = "http://steamcommunity.com/profiles/"+steamid
        
    player.save()
    print "Player logged in:", player.nickname
    
    return redirect('/stacks')
  
@login_required
def stacks(request):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')
      mumble              = MumbleWrapper.ICLMumble()      
      
      data = {'profile': Player.objects.get(uid=steamid),
	      'mumble_username': quote(Player.objects.get(uid=steamid).nickname),
	      'mumblelists': mumble.get_info()
	      }
      
      return render(request, 'matchmaking/stacks.html', data)


@login_required
def update_profile(request):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')    
    valveapi    = ValveApiWrapper.ValveApi()        
    playerstats = valveapi.get_player_exp_from_steamid(steamid)

    try:
      player_obj = Player.objects.get(uid=steamid)
    except Player.DoesNotExist: 
      print 'recalculateexp player does not exist'      
        
    player_obj.exp           = playerstats['exp']
    player_obj.nickname      = playerstats['nickname']
    player_obj.exp_n_games   = playerstats['exp_n_games']
    player_obj.exp_h_games   = playerstats['exp_h_games']
    player_obj.exp_vh_games  = playerstats['exp_vh_games']
    player_obj.exp_total_games = playerstats['total_games']
    player_obj.extra_exp_pts = playerstats['extra_exp_pts']    
    
    if request.method == 'POST':
      print request.POST['pri_role'], request.POST['alt_role']
      player_obj.pri_role = request.POST['pri_role']
      player_obj.alt_role = request.POST['alt_role']
    
    player_obj.save()
    
    return redirect('/stacks') 
    
    
    
@login_required 
def ratings(request):
      social_auth = request.user.social_auth.get(provider='steam')
      steamid     = social_auth.extra_data.get('steamid')  
      
      data = {'profile':Player.objects.get(uid=steamid)}
      
      players = Player.objects.all()  
      data['playerslist'] = []
      
      for each_player in players:
	  time_since_last_seen = datetime.utcnow() - each_player.last_updated.replace(tzinfo=None)
	  splits = str(time_since_last_seen).split(':')
	  pretty_time = ''
	  
	  if splits[0] != '0':
	    pretty_time += splits[0] + ' hours '
	    
	  if splits[1] != '0':
	    pretty_time += splits[1]+' minutes ago.'

	  data['playerslist'].append({'nickname': each_player.nickname,
				     'uid':        each_player.uid,
				     'exp':        each_player.exp,
				     'last_updated':  pretty_time
				      })
			
      data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
	
      return render(request, 'matchmaking/ratings.html', data)
