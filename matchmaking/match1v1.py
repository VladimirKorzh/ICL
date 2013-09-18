#from matchmaking.models import Player, Match1v1, Inventory, MatchInfo

#from random import randint

#import matchmaking.account

#DEBUG = True

#def action_lock_1v1match(match_id):
    ## Prevent spectators from placing bets on this match.
    ## takes bets from participating players
    #match = Match1v1.objects.get(id__exact=match_id)
    ## if both sides are ready and the match hasn't started yet
    #if match.sideaready == True and match.sidebready == True:
        #if match.info.result == 0:
            
            #if DEBUG: print "OK"                  
        #else:
          #if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result
    #else:
        #if DEBUG: print "Sides are not ready, can't lock the match:", match_id
               
#def action_decide_winner_1v1match(match_id, winner_side, enemy_pass):
    ## function marks the winner and deals with participants' bets
    #match = Match1v1.objects.get(id__exact=match_id)
    #ok = False
    

                    #if DEBUG: print "OK" 
                #else:
                    #if DEBUG: print "Password doesn't match"                                            
    #else:
        #if DEBUG: print "Match has result is wrong, what are trying to do?", match.info.result    
    
    

    
    
    
    
    
    
    
    
    
    
    
    