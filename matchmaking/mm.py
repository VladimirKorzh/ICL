import Ice 
Ice.loadSlice("/usr/share/slice/Murmur.ice", ['-I'+ Ice.getSliceDir()])
import Murmur
import os, sys, string, random, json
import urllib2
import time, datetime, calendar

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Player, Lobby, Roles, Search

# MUMBLE WRAPPER

# END MUMBLE WRAPPER    


# VAVLE API WRAPPER 
class ValveApi():
  def __init__(self):
    self.cache = None
    self.newcache = {}
    self.AllowNewQueries = True
    
    self.CacheFile = 'valve_api_cache.json'
    self.apikey = 'key=121A1CB1B99D9FA5C69DA2377E8B407F'    
    self.apiurls = {}
    self.apiurls['GetMatchHistory'] = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?'
    self.apiurls['GetPlayerSummaries'] = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?' 
    self.loadCache()    
    
  def writeCache(self):
    if len(self.newcache) > 0:
      with open(self.CacheFile, 'w') as output:
	  #print 'Writing cache'
	  json.dump(self.newcache, output)
	

  def loadCache(self):
    #print os.path.join(os.getcwd(),self.CacheFile)
    if os.path.exists(os.path.join(os.getcwd(),self.CacheFile)):
      with open(self.CacheFile, 'r') as input:
	  #print 'Loading cache'
	  self.cache = json.load(input)
    else:
      self.cache = {}
      
  def query_api(self, api2query, conditions):
    apiurl =  api2query       
    finalurl = apiurl+self.apikey+conditions    
    
    cachekey = datetime.date.today().isoformat() + apiurl + conditions
    
    if '&date_min=' in cachekey:
      cachekey = cachekey[:-len('date_min=1374442863')]
    
    #print cachekey
    #print "query:", finalurl
    
    # check if we have that query in cache
    if cachekey in self.cache.keys():
      #print 'Response found in cache', cachekey
      response = self.cache[cachekey]
    else:  
      response = None
      if self.AllowNewQueries:
	#print 'Response NOT found in cache', cachekey
	response = json.load(urllib2.urlopen(finalurl))
	self.newcache[cachekey] = response
	time.sleep(1)	        
    return response

  def get_player_name_from_steamid(self, userid):
      steamid = '&steamids=' + str(userid)      
      response = self.query_api(self.apiurls['GetPlayerSummaries'], steamid)
      personaname = None
      if response != None:
	personaname = response['response']['players'][0]['personaname']
      return personaname

# TODO ASYNCHRONOUS CALL OF THIS FUNCTION FROM WEBSITE
  def get_player_exp_from_steamid(self,userid):
    amount_of_games = {}
    amount_of_games[1] = 0
    amount_of_games[2] = 0
    amount_of_games[3] = 0
    
    exp = 0

    past = datetime.datetime.now() - datetime.timedelta(weeks = 4)
    
    timestamp = calendar.timegm(past.utctimetuple())
    #print 'Calculating Exp starting from', past
    
    for skill in range(1,4):
      
      if skill == 1:
	Q = 1
      if skill == 2:
	Q = 3
      if skill == 3:
        Q = 6
      
      conditions =  '&account_id=' + str(userid)
      conditions += '&skill='+str(skill)
      conditions += '&date_min='+str(timestamp) 
      
      response = self.query_api(self.apiurls['GetMatchHistory'], conditions)
      if response is not None and response['result']['status'] == 1:
	amount_of_games[skill] += response['result']['total_results']
      else:
	#print 'Error:', response['result']['statusDetail'][:25]	
	break
      exp += amount_of_games[skill] * Q
    
    total_games = amount_of_games[3]+amount_of_games[2]+amount_of_games[1]
    if total_games != 0:
      playerstats = {'exp':exp}
      self.debug = {'name':self.get_player_name_from_steamid(userid),
		      'n':amount_of_games[1], 'h':amount_of_games[2], 'vh':amount_of_games[3],
		      'total': total_games}
      print 'Player exp:',self.debug
      self.writeCache()
      return playerstats
            
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


# Steam auth interraction here 

def getUserAvatarUrl(request):
  steam_api_key = settings.STEAM_API_KEY
  social_auth = request.user.social_auth.get(provider='steam')
  return social_auth.extra_data.get('avatarmedium')
  
def updateUserInfo(request):
  social_auth = request.user.social_auth.get(provider='steam')
  steamid = social_auth.extra_data.get('steamid')
  
  try:
    player = Player.objects.get(uid=steamid)
  except Player.DoesNotExist:
    player = Player()
    
  player.uid      = steamid
  player.nickname = str(request.user)
  player.avatar   = social_auth.extra_data.get('avatarmedium')
  
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

# End steam auth interraction  
  
  
  
  
  
  
  
def get_open_lobbys(data): #TODO
      # get all lobbys that are not full
      alllobbies = Lobby.objects.all()
      data['openlobbys'] = []
      for lobby_obj in alllobbies:
	if Player.objects.filter(lobby=lobby_obj).count() < 5:
	  if lobby_obj.name == "Root": continue
	  lobbyinfo = {'name':         lobby_obj.name,
		      'players_count': Player.objects.filter(lobby=lobby_obj).count(),
		      'players_list':  Player.objects.filter(lobby=lobby_obj).values('nickname')}
	  data['openlobbys'].append(lobbyinfo)
	  
      return data     

      
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

  
    
    
