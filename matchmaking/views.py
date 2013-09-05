
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player


from urllib import quote

import mm

import ValveApiWrapper


def landing(request):
  if not request.user.is_authenticated():
      return redirect('/intro')
  else:
      # fix for people reloading page after update has been released.
      return login(request)

def intro(request):
      return render(request, 'intro.html')  

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
    # first we cast players name into utf to get a valid quote on their name
    # it produces %D0%AF%D0%99%D0%9A%D0%90 string which can be read by mubmle url protocol    
    player.mumble_nickname = quote( str(request.user).encode('utf8') )
        
    player.save()
    print "Player logged in:", player.nickname
    
    return redirect('/stacks')
 
 
@login_required
def profile(request, profile_id):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')  
    
    data = {'pl': Player.objects.get(id__exact=profile_id),
	    'profile': Player.objects.get(uid=steamid)
	    }
    
    print 'looking profile', profile_id
    
    return render(request,'profile_modal.html', data)
      
 
@login_required
def refresh(request):
    social_auth = request.user.social_auth.get(provider='steam')
    steamid     = social_auth.extra_data.get('steamid')    

    try:
      player_obj = Player.objects.get(uid=steamid)
    except Player.DoesNotExist: 
      print 'recalculateexp player does not exist'  
      
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
    
    if request.method == 'POST':
      print request.POST['pri_role'], request.POST['alt_role']
      player_obj.pri_role = request.POST['pri_role']
      player_obj.alt_role = request.POST['alt_role']
    
    player_obj.save()
    
    return redirect('/stacks') 
    
    
    

