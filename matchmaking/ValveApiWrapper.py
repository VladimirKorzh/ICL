
import os
import time, datetime, calendar
import json, urllib2

# used to load the steam API key 
from django.conf import settings

from matchmaking.models import ValveApiCounts

class ValveApi():
  def __init__(self):
    self.apikey    = 'key=' + settings.STEAM_API_KEY
    self.apiurls   = {}
    self.apiurls['GetMatchHistory'] = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/?'
    self.apiurls['GetPlayerSummaries'] = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?' 
    
  def query_api(self, api2query, conditions):
    apiurl =  api2query       
    finalurl = apiurl+self.apikey+conditions    
    
    cachekey = datetime.date.today().isoformat() + apiurl + conditions
    
    if '&date_min=' in cachekey:
      cachekey = cachekey[:-len('date_min=1374442863')]

    response = None

    try:
      obj = ValveApiCounts.objects.get(date=datetime.date.today())
    except ValveApiCounts.DoesNotExist:
      obj = ValveApiCounts()
      obj.date = datetime.date.today()
      obj.amount = 0
      
    if obj.amount < 100000:
      print 'Api request', finalurl    	
      response = json.load(urllib2.urlopen(finalurl))      
      obj.amount += 1
    else:
      print 'Amount of requests per day has been exceeded.'
      
    obj.save()
    time.sleep(1)	            
    return response

    
    
  # returns current player-set in-game nickname
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
	# user probably has his statistics closed to public
	break
	
	

	
      exp += amount_of_games[skill] * Q
    
    total_games = amount_of_games[3]+amount_of_games[2]+amount_of_games[1]
    
    
    ## new experience calculation formula
    #newexp = 0
    #max_skill_games = max(amount_of_games[1],amount_of_games[2],amount_of_games[3])
    
    #if max_skill_games == amount_of_games[3]:
      #newexp += 600 + max_skill_games/total_games*600
    #else if max_skill_games == amount_of_games[2]:
      #newexp += 300 + max_skill_games/total_games*300
    #else if max_skill_games == amount_of_games[1]:
      #newexp += 100 + max_skill_games/total_games*100
    

    
    playerstats = {'exp':exp,'name':self.get_player_name_from_steamid(userid),
		    'n':amount_of_games[1], 'h':amount_of_games[2], 'vh':amount_of_games[3],
		    'total': total_games}
    print 'get_player_exp_from_steamid', playerstats
    return playerstats

    
    
    