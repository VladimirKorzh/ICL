from matchmaking.models import Player, Match1v1, Inventory, MatchInfo

from random import randint

def db_create_match_info():
    inv = Inventory()
    inv.save()  
    matchinfo = MatchInfo()
    matchinfo.sideapass = randint(1000, 9999)
    matchinfo.sidebpass = randint(1000, 9999)
    matchinfo.lobbypass = randint(1000, 9999)
    matchinfo.bet_size  = inv
    matchinfo.save()
    return matchinfo     
    
def action_create_1v1match(sidea_id, sideb_id):
    # user creates a match to face his opponent with bets    
    # in the ui he\she selects the team\player for both sides
    # and this way creates an official match invitation  
    match = Match1v1()  
    match.sidea = Player.objects.get(id__exact=sidea_id)
    match.sideb = Player.objects.get(id__exact=sideb_id)
    match.info  = db_create_match_info()
    match.save()

def action_cancel_1v1match(match_id):
    # user does not want to participate in this match
    # or has other reasons not to play it.
    match = Match1v1.objects.get(id__exact=match_id)
    match.info.result = 3
    match.info.save()
    match.save()
    
def action_ready_1v1match(match_id, player_id):
    # both users see the terms and conditions of proposed
    # match and click Agree button.
    match = Match1v1.objects.get(id__exact=match_id)
    player = Player.objects.get(id__exact=player_id)
        
    # only if match hasn't started
    if match.info.result == 0:
        if match.sidea == player:
          match.sideaready = True
        if match.sideb == player:
          match.sidebready = True
   
    match.save()
   
def action_update_1v1match(match_id, common, uncommon, rare):
    # Something has been changed in match conditions    
    match = Match1v1.objects.get(id__exact=match_id)
    # only if match hasn't started
    if match.info.result == 0:
        # reset ready buttons
        match.sideaready = False
        match.sidebready = False
        match.info.bet_size.common   = common
        match.info.bet_size.uncommon = uncommon
        match.info.bet_size.rare     = rare
        match.info.bet_size.save()
        match.save()
   
def action_lock_1v1match(match_id):
    # Prevent spectators from placing bets on this match.
    # also gives players their passwords a lobby information
    match = Match1v1.objects.get(id__exact=match_id)
    if match.sideaready == True and match.sidebready == True and match.info.result == 0:
      match.info.result = 4
      match.info.save()
   