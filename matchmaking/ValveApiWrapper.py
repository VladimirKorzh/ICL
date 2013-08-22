
import os
import time, datetime, calendar
import json, urllib2

# used to load the steam API key 
from django.conf import settings

class ValveApi():
  def __init__(self):
    self.cache = {}
    self.newcache = {}
    self.AllowNewQueries = True
    
    self.CacheFile = 'valve_api_cache.json'
    self.apikey    = 'key=' + settings.STEAM_API_KEY
    print self.apikey
    self.apiurls   = {}
    self.apiurls['GetMatchHistory'] = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?'
    self.apiurls['GetPlayerSummaries'] = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?' 
    #self.loadCache()    
    
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
	print 'Api request', finalurl
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
      #self.writeCache()
      pass
      
    
    playerstats = {'exp':exp,'name':self.get_player_name_from_steamid(userid),
		    'n':amount_of_games[1], 'h':amount_of_games[2], 'vh':amount_of_games[3],
		    'total': total_games}
    print 'get_player_exp_from_steamid', playerstats
    return playerstats
            