
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Lobby, Player, Search

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
  social_auth   = request.user.social_auth.get(provider='steam')
  
  data = {'username':request.user,
	  'exp':     mm.getPlayerExp(request)}
  
  mumble              = MumbleWrapper.ICLMumble()
  data['mumblelists'] = mumble.get_info()	
    
  return render(request, 'matchmaking/stacks.html', data)

@login_required 
def ratings(request):
  data = {'username':request.user,
          'exp': mm.getPlayerExp(request)}
  
  players = Player.objects.all()  
  data['playerslist'] = []
  for each_player in players:
    data['playerslist'].append({ 'nickname': each_player.nickname,
				 'uid':      each_player.uid,
				 'exp':     each_player.exp
				})
  
  return render(request, 'matchmaking/ratings.html', data)
