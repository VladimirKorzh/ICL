import Ice 
Ice.loadSlice("/usr/share/slice/Murmur.ice", ['-I'+ Ice.getSliceDir()])
import Murmur
import os, sys, string, random, json
import urllib2
import time, datetime, calendar


from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player, Lobby, Roles, Search

import MumbleWrapper
import ValveApiWrapper


# Stats for 08/18/2013 
# 646 taburetka^_^
# 574 ICR.HoSi
# 503 ICR.korzh
# 461 ICR.Rock'n'Rolla
# 429 ICR.kowka
# 327 ICR.MARIO
# 310 ICR.Immortal
# 309 ICR.LuckyMan
# 263 RockNaR
# 236 ICR.Axe.Heart
# 145 ICR.MiniSpy v.2.0

def getUserAvatarUrl(request):
  steam_api_key = settings.STEAM_API_KEY
  social_auth = request.user.social_auth.get(provider='steam')
  return social_auth.extra_data.get('avatar')
  
def updateUserInfo(request):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid = social_auth.extra_data.get('steamid')
  
  try:
    player = Player.objects.get(uid=steamid)
  except Player.DoesNotExist:
    player = Player()
    
  player.uid      = steamid
  player.nickname = str(request.user)
  player.avatar   = social_auth.extra_data.get('avatar')
  
  #try:
    #afklobby = Lobby.objects.get(name='AFK')     
  #except Lobby.DoesNotExist:
    #afklobby = Lobby(name='AFK')
    #afklobby.save()
    
  #player.lobby = None
  
  # create roles for user
  if player.roles == None:
    roles = Roles()
    roles.save()
    player.roles = roles    
  
  player.save()
  print "Player logged in:", player


  
  
  
  
  

  

  
  
 

      
def _generate_id(size=6, chars=string.digits):#TODO  
  return ''.join(random.choice(chars) for x in range(size))
  
  
def startsearch(request):#TODO  
    response = {"HTTPRESPONSE":1}
    print "Searching for user:", request.user
    #print "all players:", Player.objects.all()
    
    player_asking = Player.objects.get( nickname=request.user ) 
    newsearch = Search( player=player_asking )
    newsearch.save()
      
    json_data = json.dumps(response)
    return HttpResponse(json_data, mimetype="application/json")	
  
  
def getmatch(request):#TODO  
    KORZH_DEBUG = True
    response = {}
    print "getmatch for:", request.user
    player_asking = Player.objects.get(nickname=request.user) 
    search        = Search.objects.get(player=player_asking)
    
    if len(search.response) or KORZH_DEBUG:
      response["HTTPRESPONSE"] = 1
      response["lobby"] = search.response
    else:
      response["HTTPRESPONSE"] = 0
      
    search.delete()
    
    json_data = json.dumps(response)
    return HttpResponse(json_data, mimetype="application/json")	  

    
@login_required
def getplayerexp(request):
      valveapi = ValveApiWrapper.ValveApi()
      social_auth = request.user.social_auth.get(provider='steam')
      playerstats = valveapi.get_player_exp_from_steamid(social_auth.extra_data.get('steamid'))
      
      response = {}
      response['exp'] = str(playerstats['exp'])
      json_data = json.dumps(response)
      return HttpResponse(json_data, mimetype="application/json")  
    
    