

#import os, sys, string, random, json
#import urllib2

#from datetime import tzinfo, datetime

#from django.conf import settings
#from django.http import HttpResponse
#from django.contrib.auth.decorators import login_required

##from matchmaking.models import Player
##from betting.models import Bet, Bidder 


##import MumbleWrapper
##import ValveApiWrapper


### used as a way to get whatever is stored in db
### for that user. may return old value
##@login_required
##def getPlayerExp(request):      
    ##try:
      ##player = Player.objects.get(nickname=request.user)
      ##exp = player.exp
	
    ##except Player.DoesNotExist:
      ##print request.user, 'not found in db'
      ##updateUserInfo(request)
      ##exp = 0
      
    ##return exp


  
  
##def getUserAvatarUrl(request):
  ##steam_api_key = settings.STEAM_API_KEY
  ##social_auth = request.user.social_auth.get(provider='steam')
  ##return social_auth.extra_data.get('avatar')    
  
  
##@login_required    
##def getchannelsinfo(request):    
      ##mumble = MumbleWrapper.ICLMumble()
      ##response = mumble.get_info()
      
      ##json_data = json.dumps(response)
      ##return HttpResponse(json_data, mimetype="application/json")  

## Stats for 08/18/2013 
## 646 taburetka^_^
## 574 ICR.HoSi
## 503 ICR.korzh
## 461 ICR.Rock'n'Rolla
## 429 ICR.kowka
## 327 ICR.MARIO
## 310 ICR.Immortal
## 309 ICR.LuckyMan
## 263 RockNaR
## 236 ICR.Axe.Heart
## 145 ICR.MiniSpy v.2.0 

      
##def _generate_id(size=6, chars=string.digits):#TODO  
  ##return ''.join(random.choice(chars) for x in range(size))
  
  
##def startsearch(request):#TODO  
    ##response = {"HTTPRESPONSE":1}
    ##print "Searching for user:", request.user
    ###print "all players:", Player.objects.all()
    
    ##player_asking = Player.objects.get( nickname=request.user ) 
    ##newsearch = Search( player=player_asking )
    ##newsearch.save()
      
    ##json_data = json.dumps(response)
    ##return HttpResponse(json_data, mimetype="application/json")	
  
  
##def getmatch(request):#TODO  
    ##KORZH_DEBUG = True
    ##response = {}
    ##print "getmatch for:", request.user
    ##player_asking = Player.objects.get(nickname=request.user) 
    ##search        = Search.objects.get(player=player_asking)
    
    ##if len(search.response) or KORZH_DEBUG:
      ##response["HTTPRESPONSE"] = 1
      ##response["lobby"] = search.response
    ##else:
      ##response["HTTPRESPONSE"] = 0
      
    ##search.delete()
    
    ##json_data = json.dumps(response)
    ##return HttpResponse(json_data, mimetype="application/json")	  

    

    