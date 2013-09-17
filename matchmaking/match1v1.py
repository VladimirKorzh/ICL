from matchmaking.models import Player, Match1v1, Inventory, MatchInfo

from random import randint

import matchmaking.account

DEBUG = True

def db_create_match_info():
    inv = Inventory()
    inv.save()  
    matchinfo = MatchInfo()
    matchinfo.sideapass = randint(1000, 9999)
    matchinfo.sidebpass = randint(1000, 9999)
    matchinfo.lobbypass = randint(1000, 9999)
    matchinfo.bet_size  = inv
    matchinfo.save()
    if DEBUG: print "OK"
    return matchinfo     
    
def action_create_1v1match(sidea_id, sideb_id):
    # user creates a match to face his opponent with bets    
    # in the ui he\she selects the team\player for both sides
    # and this way creates an official match invitation  
    match = Match1v1()  
    
    # check that the sides are not the same
    if sidea_id != sideb_id:
        match.sidea = Player.objects.get(id__exact=sidea_id)
        match.sideb = Player.objects.get(id__exact=sideb_id)
        match.info  = db_create_match_info()
        match.save()
        if DEBUG: print "OK"
    else:
        if DEBUG: print "Can't create match1v1 with same player on both sides"

def action_cancel_1v1match(match_id):
    # user does not want to participate in this match
    # or has other reasons not to play it.
    match = Match1v1.objects.get(id__exact=match_id)
    match.info.result = 3
    match.info.save()
    match.save()
    if DEBUG: print "OK"
    
def action_ready_1v1match(match_id, player_id, value=True):
    # both users see the terms and conditions of proposed
    # match and click Agree button.
    match = Match1v1.objects.get(id__exact=match_id)
    player = Player.objects.get(id__exact=player_id)
          
    # only if match hasn't started
    if match.info.result == 0:
        if match.sidea == player:          
          match.sideaready = value
        if match.sideb == player:
          match.sidebready = value
        match.save()
        if DEBUG: print "OK"
    else:
        if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result
          
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
        if DEBUG: print "OK"
    else:
        if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result
   
def action_lock_1v1match(match_id):
    # Prevent spectators from placing bets on this match.
    # takes bets from participating players
    match = Match1v1.objects.get(id__exact=match_id)
    # if both sides are ready and the match hasn't started yet
    if match.sideaready == True and match.sidebready == True:
        if match.info.result == 0:
            for player in [match.sidea, match.sideb]:
                # Lets just make sure that the players have these items on their accounts
                if player.inventory.common >= match.info.bet_size.common and player.inventory.uncommon >= match.info.bet_size.uncommon and player.inventory.rare >= match.info.bet_size.rare:                          
                    pass
                else:
                    action_ready_1v1match(match_id, player.id, False)
                    if DEBUG: print "Player doesn't have enough items in his inventory", player.id            
                    return;                  
            # if we got to here then both players are ok
            # take their items
            for player in [match.sidea, match.sideb]:
                matchmaking.account.db_player_inventory_action(player.id, 1, match.info.bet_size.id)
            # start the match
            match.info.result = 4
            match.info.save()
            if DEBUG: print "OK"                  
        else:
          if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result
    else:
        if DEBUG: print "Sides are not ready, can't lock the match:", match_id
               
def action_decide_winner_1v1match(match_id, winner_side, enemy_pass):
    # function marks the winner and deals with participants' bets
    match = Match1v1.objects.get(id__exact=match_id)
    ok = False
    
    # check for valid result and passwords
    if match.info.result == 4:    
    
        for data in [{'side':1, 'pass':match.info.sidebpass, 'winner':match.sidea}, {'side':2, 'pass':match.info.sideapass, 'winner':match.sideb}]:    
            if winner_side == data['side']:
                if enemy_pass == data['pass']:
                    match.info.result = data['side'] 
                    match.info.save()
                    
                    # award the winner twice the bet amount
                    matchmaking.account.db_player_inventory_action(data['winner'].id, 0, match.info.bet_size.id)
                    matchmaking.account.db_player_inventory_action(data['winner'].id, 0, match.info.bet_size.id)
                    if DEBUG: print "OK" 
                else:
                    if DEBUG: print "Password doesn't match"                                            
    else:
        if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result    
    
    

    
    
    
    
    
    
    
    
    
    
    
    