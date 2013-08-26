
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Player

import mm
import MumbleWrapper
import ValveApiWrapper


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

@login_required
def bets(request, bet_id=None, action='mybets'):
  # find id
  # create bet
  # mybets
  
      data = {'username': request.user,
	      'exp':       mm.getPlayerExp(request)}  

      if action:
	data['action'] = action	      
	      
      if bet_id:
	data['bet_id'] = bet_id

      return render(request, 'matchmaking/bets.html', data)

@login_required 
def ratings(request):
      data = {'username':request.user,
	      'exp': mm.getPlayerExp(request)}
      
      players = Player.objects.all()  
      data['playerslist'] = []
      for each_player in players:
	  data['playerslist'].append({'nickname': each_player.nickname,
				     'uid':       each_player.uid,
				     'exp':       each_player.exp,
				     'last_seen': each_player.last_seen
				    })
			
      data['playerslist'] = sorted(data['playerslist'], key=lambda pl:pl['exp'], reverse=True)
      n = 1
      for each in data['playerslist']:
	each['position'] = n
	n+=1
	
      return render(request, 'matchmaking/ratings.html', data)
