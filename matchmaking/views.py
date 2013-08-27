
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

      
      
#############################################################
# BETTING PART
#############################################################

def get_player_id_in_internal_database(playername):
    # performs a lookup of current login in internal db
    # and returns the id. FIX for weird usernames
    return Player.objects.get(nickname=playername).id

    
@login_required
def remove_bet(request, bet_id):
    bet2delete = Bet.objects.filter(id__exact=bet_id)[0]
    
    # check if we are the owner of this bet
    # only owner can order a delete call.
    if get_player_id_in_internal_database(request.name) == bet2delete.owner.id:    
      bet2delete.delete()
    
    return redirect('/bets')

    
@login_required
def cancel_bet(request, bet_id):
    player_id = get_player_id_in_internal_database(request.name)  
  
    # if we are able to find the persons bid on this bet, than delete it.
    # account for multiple returned rows to prevent multiple bets being
    # submitted by one person.
    for each in Bidder.objects.filter(player__id__exact=player_id, bet__id__exact = bet_id):
	each.delete()
      
    return redirect('/bets')    
    
    
@login_required
def close_bet(request, bet_id):  
    # find the bet that we are about to close
    bet2close = Bet.objects.filter(id__exact=bet_id)[0]	    
    
    # find all the bidders on this bet
    a = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A')
    b = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B')	    
    
    # only allow the owner of the bet to close it
    if get_player_id_in_internal_database(request.name) == bet2close.owner.id:
      
      # check that both sides have equal amount of bidders
      # and also check that the bet has any bidders at all
      if len(a) == len(b) and len(a) and len(b):	
	bet2close.status = 'CLOSED'
	
	# Generate passwords for both sides
	bet2close.sideapass = randint(1000, 9999)
	bet2close.sidebpass = randint(1000, 9999)	
	bet2close.save()
	
    return redirect('/bets')	
    
    
@login_required    
def decide_bet(request, bet_id, side, password):
    player_id = get_player_id_in_internal_database(request.name)
    
    # bet result can be decided by any person that provides the 
    # correct password. It is absolutely important to keep it 
    # this way in order to avoid scams.
    
    # find the bet that we are about to decide result of
    res = Bet.objects.filter(id__exact=bet_id)[0]
    
    # don't forget to set its status
    res.status = 'PRIZES'    
    
    # if the password matches the password for the opposite side
    # than we seal the deal and pass it on the bot for giving
    # out prizes.
    if side == 'a' and str(password) == str(res.sidebpass):
      res.result = 'A'
      res.save()
      
    if side == 'b' and str(password) == str(res.sideapass):
      res.result = 'B'
      res.save()
    
    return redirect('/bets')    

    
@login_required
def takeside_bet(request, bet_id, side):
    player_id = get_player_id_in_internal_database(request.name)
    
    # check if the user has already placed his bid on this
    # bet first, to prevent multiple bidding.
    bid = None
    res = Bidder.objects.filter(id__exact=bet_id, player__id__exact=player_id)

    # if we have matched any bidders at all we'd rather delete them all
    # to prevent any bugs related to dublication at all.    
    if len(res):
      #print 'Bidder found -> updating his record'
      for each in res:
	each.delete()
            
    # if we haven't matched any bidders than we have to create a new bidder
    # for this bet and this user. 
    bid = Bidder()
    bid.status = 'COLLECTION'
    bid.player = Player.objects.get(id__exact=player_id)
    bid.bet    = Bet.objects.get(id__exact=bet_id)
	
    if side == 'a':
      bid.side = 'A'
    if side == 'b':
      bid.side = 'B'
      
    bid.save()    
    return redirect('/bets')      
            
@login_required
def create_new(request):
    # only allow creation of new bets on POST requests
    # otherwise skip the whole thing.
    if request.method == 'POST':
	bet = Bet()
	bet.amount      = request.POST['amount']
	bet.item_rarity = request.POST['rarity']
	bet.result      = 'NOTDECIDED'
	bet.status      = 'OPEN'
	bet.owner       = Player.objects.get(nickname=name)
	bet.save()
	
    return redirect('/bets')  
    
@login_required    
def mybets(request, bet_id=None):
      player_id = get_player_id_in_internal_database(request.name)
      
      # data structure that will hold information that we pass on
      # to render call
      data = {'username': request.user,
	      'exp':       mm.getPlayerExp(request),
	      'results': []
	      }  
      
      # used to store ids of bets that we have already appended
      # to the return data structure.
      selection_bets_ids = []
      
      # holds the Bet objects that we actually iterate over to produce
      # this return data structure.
      selection = []
	
      # find bets that have this player as owner.
      ownbets = Bet.objects.filter(owner__id__exact=player_id)
      for each in ownbets:
	# add them to our temp structures
	selection_bets_ids.append(each.id)
	selection.append(each)
    
      # find bets that have this player as a bidder	
      # by finding all bids that have this player and jumping
      # over to respective bets.
      ownbids = Bidder.objects.filter(player__id__exact=player_id)
      for each in ownbids:	
	bet = Bet.objects.get(id__exact=each.bet_id)
	
	# if we have never added this Bet into our return
	# data structure than add it there and mark its id
	if bet.id not in selection_bets_ids:  
	  selection_bets_ids.append(bet.id)
	  selection.append(bet)
      
      # if the user has provided a specific bet id to show, then add it
      # to selection list too
      if bet_id:
	for each in Bet.objects.filter(id__exact=bet_id):
	  selection_bets_ids.append(each.id)
	  selection.append(each)	  
      
      # after we have prepared our selection we have to fill in some extra
      # information in.
      for each in selection:
	
	# append bidders to each bet.
	each.a = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A')
	each.b = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B')
	  
	# mark the bet if the requester is its owner
	if each.owner == Player.objects.get(nickname = name):
	  each.isowner = True
		
	# show side passwords only if the person if on that side.
	if len(Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A', player__id__exact=player_id)):
	  each.passwd = each.sideapass
	  
	if len(Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B', player__id__exact=player_id)):
	  each.passwd = each.sidebpass	      
	  
	# otherwise leave those fields empty
	each.sideapass = ''
	each.sidebpass = ''	      
	  
	# append the record to the data passed to render call
	data['results'].append(each)
	
      # presort the results so that the higher ids are on top.
      data['results'] = sorted(data['results'], key=lambda bet:bet.id, reverse=True)      
      return render(request, 'matchmaking/bets.html', data)    

#########################################################################
# END OF BETTING PART
#########################################################################
      
          
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
