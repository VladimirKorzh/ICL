
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from matchmaking.models import Player

import mm
import MumbleWrapper


def landing(request):
  if not request.user.is_authenticated():
      return redirect('/intro')
  else:
      return redirect('/stacks')

def intro(request):
      return render(request, 'matchmaking/intro.html')  
  
@login_required  
def login(request):
      mm.updateUserInfo(request)
      return redirect('/stacks')
  
@login_required
def stacks(request):
      social_auth = request.user.social_auth.get(provider='steam')
      
      data = {'username': request.user,
	      'exp':       mm.getPlayerExp(request)}
      
      mumble              = MumbleWrapper.ICLMumble()
      data['mumblelists'] = mumble.get_info()
      mumble = None      

      return render(request, 'matchmaking/stacks.html', data)

           
from datetime import tzinfo, timedelta, datetime
@login_required 
def ratings(request):
      data = {'username':request.user,
	      'exp': mm.getPlayerExp(request)}
      
      players = Player.objects.all()  
      data['playerslist'] = []
      for each_player in players:
	
	  time_since_last_seen = datetime.utcnow() - each_player.last_seen.replace(tzinfo=None)
	  splits = str(time_since_last_seen).split(':')
	  pretty_time = ''
	  
	  if splits[0] != '0':
	    pretty_time += splits[0] + ' hours '
	    print splits[0]
	    
	  if splits[1] != '0':
	    pretty_time += splits[1]+' minutes ago.'
	  
	  data['playerslist'].append({'nickname': each_player.nickname,
				     'uid':       each_player.uid,
				     'exp':       each_player.exp,
				     'last_seen': pretty_time
				      })
			
      data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
      n = 1
      for each in data['playerslist']:
	each['position'] = n
	n+=1
	
      return render(request, 'matchmaking/ratings.html', data)
