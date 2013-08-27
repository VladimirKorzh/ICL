

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from betting.models import Bet, Bidder
from matchmaking.models import Player
from matchmaking import mm


from random import randint


def get_player_id_in_internal_database(playername):
    # performs a lookup of current login in internal db
    # and returns the id. FIX for weird usernames
    return Player.objects.get(nickname=playername).id

    
@login_required
def remove_bet(request, bet_id):
    bet2delete = Bet.objects.filter(id__exact=bet_id)[0]
    
    # check if we are the owner of this bet
    # only owner can order a delete call.
    if get_player_id_in_internal_database(request.user) == bet2delete.owner.id:    
      bet2delete.delete()
    
    return redirect('/bets')

    
@login_required
def cancel_bet(request, bet_id):
    player_id = get_player_id_in_internal_database(request.user)  
  
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
    if get_player_id_in_internal_database(request.user) == bet2close.owner.id:
      
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
    player_id = get_player_id_in_internal_database(request.user)
    
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
    player_id = get_player_id_in_internal_database(request.user)
    
    # check if the user has already placed his bid on this
    # bet first, to prevent multiple bidding.    
    cancel_bet(request, bet_id)
    
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
    player_id = get_player_id_in_internal_database(request.user)
  
    # only allow creation of new bets on POST requests
    # otherwise skip the whole thing.
    if request.method == 'POST':
	bet = Bet()
	bet.amount      = request.POST['amount']
	bet.item_rarity = request.POST['rarity']
	bet.result      = 'NOTDECIDED'
	bet.status      = 'OPEN'
	bet.owner       = Player.objects.get(id__exact=player_id)
	bet.save()
	
    return redirect('/bets')  
    
@login_required    
def mybets(request):
      player_id = get_player_id_in_internal_database(request.user)
      
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
      if request.method == 'POST':
	bet_id = None
	# make sure the value is not empty
	if request.POST['bet_id'] != '':
	  bet_id = request.POST['bet_id']      
	  
	if bet_id:
	  for each in Bet.objects.filter(id__exact=bet_id):
	    if each.id not in selection_bets_ids:
	      selection_bets_ids.append(each.id)
	      selection.append(each)
      
      # after we have prepared our selection we have to fill in some extra
      # information in.
      for each in selection:
	
	# append bidders to each bet.
	each.a = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A')
	each.b = Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B')
	  
	# mark the bet if the requester is its owner
	if each.owner == Player.objects.get(id__exact=player_id):
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
      return render(request, 'betting/bets.html', data)    