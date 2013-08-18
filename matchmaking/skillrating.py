import json
import urllib2
import os
import time
import datetime
import calendar

# ICR.korzh 76561198065555552

class ValveApi():
  def __init__(self):
    self.cache = None
    self.AllowNewQueries = False
    
    self.CacheFile = 'valve_api_cache.json'
    self.apikey = 'key=121A1CB1B99D9FA5C69DA2377E8B407F'    
    self.apiurls = {}
    self.apiurls['GetMatchHistory'] = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?'
    self.apiurls['GetPlayerSummaries'] = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?' 
    self.loadCache()

  def writeCache(self):
      # TODO    
      # therer might be more efficient way
      # of doing that. Maybe writeappend
      with open(self.CacheFile, 'w+') as output:
	  print 'Writing cache'
	  json.dump(self.cache, output)

  def loadCache(self):
    if os.path.exists(os.path.join(os.getcwd(),self.CacheFile)):
      with open(self.CacheFile, 'r') as input:
	  print 'Loading cache'
	  self.cache = json.load(input)
    else:
      self.cache = {}

  
  def query_api(self, api2query, conditions):
    apiurl =  api2query       
    finalurl = apiurl+self.apikey+conditions    
    cachekey = datetime.date.today().isoformat() + apiurl + conditions
    
    # check if we have that query in cache
    if cachekey in self.cache.keys():
      #print 'Response found in cache',str(playerid),str(skill)
      response = self.cache[cachekey]
    else:  
      response = None
      if self.AllowNewQueries:
	#print 'Response NOT found in cache',str(playerid),str(skill)
	response = json.load(urllib2.urlopen(finalurl))
	time.sleep(1)
	if response['result']['status'] == 1:
	  self.cache[cachekey] = response  
      
    return response


# TODO Might need replacement!    
  def get_player_name(self, userid):
      steamid = '&steamids=' + str(userid)      
      response = self.query_api(self.apiurls['GetPlayerSummaries'], steamid)
      personaname = None
      if response != None and response['results']['status'] == 1:
	personaname = response['response']['players'][0]['personaname']
      return personaname


# TODO Transfer over to server
  def get_player_exp(self,userid):
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
      
      conditions = '&account_id=' + str(userid)
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
      playerstats = {'name':self.get_player_name(userid), 'exp':exp,
			 'n':amount_of_games[1], 'h':amount_of_games[2], 'vh':amount_of_games[3],
			 'total': total_games,
			 'probVH':float(amount_of_games[3])/total_games,
			 'probH': float(amount_of_games[2])/total_games,
			 'probN': float(amount_of_games[1])/total_games}
      self.ranking.append(playerstats)
      return playerstats
      
if __name__ == '__main__':
  api = ValveApi()
  
  api.get_player_exp(76561198046413714)
  api.get_player_exp(76561198065555552)
  api.get_player_exp(76561198078129877)
  api.get_player_exp(76561198029978161)
  api.get_player_exp(76561198074682637)
  api.get_player_exp(76561198076606162)
  api.get_player_exp(76561198075034663)
  api.get_player_exp(76561198078182151)  
  api.get_player_exp(76561198087333575)    
  api.get_player_exp(76561198096939627)      
  api.get_player_exp(76561197988152489)
  api.get_player_exp(76561198042576722)
  api.get_player_exp(76561198053676979)  
  api.get_player_exp(76561198082692508)  
  api.get_player_exp(76561198096053872)  
    
  api.writeCache()
  