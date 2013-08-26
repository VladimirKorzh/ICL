
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Player, Bet, Bidder

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
      name = request.user  
      data = {'username': request.user,
	      'exp':       mm.getPlayerExp(request)}  
      
      data['results'] = []      
      dataset = []
      
      
      
      if action == 'mybets':
	for each in Bet.objects.filter(owner__nickname__exact=name):
	  each.a = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A')
	  each.b = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B')
	  if each.owner == Player.objects.get(nickname = name):
	    each.isowner = True
	  data['results'].append(each)

	
      if action == 'show':	
	data['results'] = []
	
	for each in Bet.objects.filter(id__exact=bet_id):
	  each.a = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A')
	  each.b = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B')
	  if each.owner == Player.objects.get(nickname = name):
	    each.isowner = True	  
	  data['results'].append(each)	
		
      if (action == 'cancelbet'):
	  res = Bidder.objects.filter(player__nickname__exact=name, id__exact=bet_id)
	  if len( res ) == 0:
	    print 'nothing to cancel'
	  else:
	    res[0].delete()
	  return redirect('/bets/show/'+bet_id)
	
      if (action == 'takesidea' or action == 'takesideb') and bet_id:
	    res = Bidder.objects.filter(player__nickname__exact=name, id__exact=bet_id)
	    if len( res ) == 0:
		print 'no bidders matched -> creating new'
		bid = Bidder()
		bid.status = 'COLLECTION'
		bid.player = Player.objects.get(nickname=name)
		bid.bet    = Bet.objects.get(id__exact=bet_id)

	    else:
		print 'bidders matched -> updating'
		bid = res[0]
		
	    if action == 'takesidea':
	      bid.side = 'A'
	    if action == 'takesideb':
	      bid.side = 'B'
	    bid.save()	    
	    return redirect('/bets/show/'+bet_id)

	
	

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
