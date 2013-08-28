
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
def update_bet_status(request, bet_id):
  # function that allows bet to transition from one state to
  # the other. Open -> Collecting -> Ready -> Awarding -> Done
  
  # find the bet that we are dealing with
  bet = Bet.objects.filter(id__exact=bet_id)[0]
    
  if bet.status == 'Collecting' or bet.status == 'Awarding':
    # check if we have already collected\awarded all the items\players
    res = Bidder.objets.filter(bet_id__exact=bet_id)
    ok = True
    for each in res:
      if each.status != 'OK':
	ok = false
	break
	
    if ok:
      if bet.status == 'Collecting':
	bet.status = 'Ready'

      if bet.status == 'Awarding':
	bet.status = 'Done'
	
      bet.save()    
    
    
@login_required
def close_bet(request, bet_id):  
    # find the bet that we are about to close
    bet2close = Bet.objects.filter(id__exact=bet_id)[0]	    
    
    # only allow to close the Open bets
    if bet2close.status == 'Open':
      
      # only allow the owner of the bet to close it
      if get_player_id_in_internal_database(request.user) == bet2close.owner.id:
      
	# find all the bidders on this bet
	a = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='A')
	b = Bidder.objects.filter(bet_id__exact=bet_id, side__exact ='B')	        
      
	# check that both sides have equal amount of bidders
	# and also check that the bet has any bidders at all
	if len(a) == len(b) and len(a) and len(b):	
	  bet2close.status = 'Collecting'
	  
	  # mark all the bidders for collection from bot
	  for each in a:
	    each.status = 'Collect'
	    each.save()
	    
	  for each in b:
	    each.status = 'Collect'
	    each.save()
	  
	  # Generate passwords for both sides
	  bet2close.sideapass = randint(1000, 9999)
	  bet2close.sidebpass = randint(1000, 9999)	
	  bet2close.save()
	
    return redirect('/bets')	
    
@login_required
def remove_bet(request, bet_id):
    bet2delete = Bet.objects.filter(id__exact=bet_id)[0]
    
    # only allow users to remove open bets
    if bet2delete.status == 'Open':    
      # check if we are the owner of this bet
      # only owner can order a delete call.
      if get_player_id_in_internal_database(request.user) == bet2delete.owner.id:    
      
	# remove its bidders as well
	for each in Bidder.objects.filter(bet_id__exact=bet_id):
	  each.delete()
	
	bet2delete.delete()

    return redirect('/bets')

    
@login_required
def cancel_bet(request, bet_id):
    player_id = get_player_id_in_internal_database(request.user)  
  
    # only allow cancelling bets if the bet is open
    res = Bet.objects.filter(id__exact=bet_id)[0]  
    if res.status == 'Open':
      # if we are able to find the persons bid on this bet, than delete it.
      # account for multiple returned rows to prevent multiple bets being
      # submitted by one person.
      for each in Bidder.objects.filter(player__id__exact=player_id, bet__id__exact = bet_id):
	  each.delete()
      
    return redirect('/bets')    
    

@login_required    
def decide_bet(request, bet_id, side, password):
    player_id = get_player_id_in_internal_database(request.user)
    
    # bet result can be decided by any person that provides the 
    # correct password. It is absolutely important to keep it 
    # this way in order to avoid scams.
    
    print bet_id, side, password
    # find the bet that we are about to decide result of
    res = Bet.objects.filter(id__exact=bet_id)[0]
    
    # only allow decision to be made once all the items were collected
    if res.status == 'Ready':
      # don't forget to set its status
      res.status = 'Awarding'    
                 
      # if the password matches the password for the opposite side
      # than we seal the deal and pass it on the bot for giving
      # out prizes.
      if side == 'a' and str(password) == str(res.sidebpass):
	res.result = 'A'
	res.save()
	
      if side == 'b' and str(password) == str(res.sideapass):
	res.result = 'B'
	res.save()
    
      # if the provided information was correct and we have a winner side
      if res.result != '?':
	# mark winners for awarding
	for each in Bidder.objects.filter(bet_id__exact=bet_id, side__exact=res.result):
	  each.status = 'Award'
	  each.save()
    
    return redirect('/bets')    

    
@login_required
def takeside_bet(request, bet_id, side):
    player_id = get_player_id_in_internal_database(request.user)
    
    # only allow changing sides if the bet is open
    res = Bet.objects.filter(id__exact=bet_id)[0]
    if res.status == 'Open':      
      # check if the user has already placed his bid on this
      # bet first, to prevent multiple bidding.    
      cancel_bet(request, bet_id)
      
      # if we haven't matched any bidders than we have to create a new bidder
      # for this bet and this user. 
      bid = Bidder()
      bid.status = 'OK'
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
	bet.rarity      = request.POST['rarity']
	bet.result      = '?'
	bet.status      = 'Open'
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
      
      # update bet status for each bet that we are looking at
      for each in selection_bets_ids:
	  update_bet_status(request, each)
      
      # after we have prepared our selection we have to fill in some extra
      # information in.
      for each in selection:
	
	# append bidders to each bet.
	each.a = []
	for every in Bidder.objects.filter(bet_id__exact=each.id, side__exact ='A'):
	  each.a.append((every.player.nickname, every.status));
	
	each.b = []
	for every in Bidder.objects.filter(bet_id__exact=each.id, side__exact ='B'):
	  each.b.append((every.player.nickname, every.status));
	  
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
