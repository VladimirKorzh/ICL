
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from django.conf import settings
from django.http import HttpResponse

from matchmaking.models import Player, Bet, Bidder

import mm
import MumbleWrapper
import ValveApiWrapper

from random import randint

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
def bets(request, bet_id=None, action='mybets', passwd=None):
  # find id
  # create bet
  # mybets
      name = request.user  
      data = {'username': request.user,
	      'exp':       mm.getPlayerExp(request)}  
      
      data['results'] = []      
      dataset = []
      
      if request.method == 'POST':
	print 'createbet'	  
	print 'request post'
	print request.POST
	bet = Bet()
	bet.amount = request.POST['amount']
	bet.item_rarity = request.POST['rarity']
	bet.result = 'NOTDECIDED'
	bet.status = 'OPEN'
	bet.owner = Player.objects.get(nickname=name)
	bet.save()
	return redirect('/bets')	
      
      
      if action == 'mybets':
	  selection = []
	  selection.extend( Bet.objects.filter(owner__nickname__exact=name) )
	
	  for each in Bidder.objects.filter(player__nickname__exact=name):
	    selection.extend(Bet.objects.filter(id__exact=each.bet_id))
		
	  for each in selection:
	    each.a = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A')
	    each.b = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B')
	      
	    if each.owner == Player.objects.get(nickname = name):
	      each.isowner = True
	    	    
	    if len(Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A', player__nickname__exact=name)):
	      each.passwd = each.sideapass
	      
	    if len(Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B', player__nickname__exact=name)):
	      each.passwd = each.sidebpass	      
	      
	    each.sideapass = ''
	    each.sidebpass = ''	      
	      
	    data['results'].append(each)
	    
	  data['results'] = sorted(data['results'], key=lambda bet:bet.id, reverse=True)
	  
	  return render(request, 'matchmaking/bets.html', data)
	
      if action == 'show':	
	  data['results'] = []
	  
	  for each in Bet.objects.filter(id__exact=bet_id):
	    each.a = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A')
	    each.b = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B')
	    
	    if each.owner == Player.objects.get(nickname = name):
	      each.isowner = True
	    	    
	    if len(Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A', player__nickname__exact=name)):
	      each.passwd = each.sideapass
	      
	    if len(Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B', player__nickname__exact=name)):
	      each.passwd = each.sidebpass	      
	      
	    each.sideapass = ''
	    each.sidebpass = ''
	    
	    data['results'].append(each)
	    
	  return render(request, 'matchmaking/bets.html', data)	

	    
		
      if action == 'deletebet':
	    bet2delete = Bet.objects.filter(id__exact=bet_id)[0]
	    bet2delete.delete()
	    return redirect('/bets')
	    
		
      if action == 'closebetting':
	    bet2close = Bet.objects.filter(id__exact=bet_id)[0]	    
	    a = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A')
	    b = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B')	    
	    if len(a) == len(b) and len(a) and len(b):
	      bet2close.status = 'CLOSED'
	      bet2close.sideapass = randint(1000, 9999)
	      bet2close.sidebpass = randint(1000, 9999)
	      bet2close.save()
	    return redirect('/bets')	

      if action == 'winnersidea' or action == 'winnersideb':
	    res = Bet.objects.filter(id__exact=bet_id)[0]
	    res.status = 'PRIZES'	    
	    user_passwd = passwd
	    
	    print res.sideapass, res.sidebpass
	    print user_passwd == res.sideapass, user_passwd == res.sidebpass
	    print action, user_passwd
	    
	    if action == 'winnersidea' and str(user_passwd) == str(res.sidebpass):
	      res.result = 'A'
	      res.save()
	     
	    if action == 'winnersideb' and str(user_passwd) == str(res.sideapass):
	      res.result = 'B'
	      res.save()
	    
	    return redirect('/bets')	
	    
      if action == 'cancelbet':
	    res = Bidder.objects.filter(player__nickname__exact=name, id__exact=bet_id)
	    if len( res ) == 0:
	      print 'nothing to cancel'
	    else:
	      res[0].delete()
	    return redirect('/bets')	  
	
      if action == 'takesidea' or action == 'takesideb':
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
	    return redirect('/bets')

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
