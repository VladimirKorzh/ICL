from matchmaking.models import Player, Inventory, Rating, BotRequest
import ValveApiWrapper

from datetime import timedelta
from django.utils import timezone

import snippets

DEBUG = True

def db_create_player(steamid):
    player = Player()
    inv = Inventory()
    inv.save()
    rating = Rating()
    rating.save()
    player.inventory = inv
    player.rating    = rating 
    player.uid = steamid
    player.save()    
    return player

    
def db_player_inventory_action(player_id, action, inv_id):
    player = Player.objects.get(id__exact=player_id)
    inv    = Inventory.objects.get(id__exact=inv_id)
    
    if action == 0:
        player.inventory.common   += inv.common
        player.inventory.uncommon += inv.uncommon
        player.inventory.rare     += inv.rare
        if DEBUG: print "OK. Items given"
      
    if action == 1:
        player.inventory.common   -= inv.common
        player.inventory.uncommon -= inv.uncommon
        player.inventory.rare     -= inv.rare
        if DEBUG: print "OK. Items taken"
      
    player.inventory.save()
      
def db_refresh_player_rating(steamid):
    vapi = ValveApiWrapper.ValveApi()
    player_obj    = Player.objects.get(uid=steamid)
    player_rating = player_obj.rating    
    
    playerstats = vapi.get_player_exp_from_steamid(steamid)  
    
    player_obj.nickname        = playerstats['nickname']
    player_obj.mumble_nickname = snippets.escape_username(playerstats['nickname'])
    player_rating.skillrating = playerstats['exp']
    player_rating.normal      = playerstats['exp_n_games']
    player_rating.high        = playerstats['exp_h_games']
    player_rating.veryhigh    = playerstats['exp_vh_games']
    player_rating.month_games = playerstats['total_games']    
    player_rating.extra_pts   = playerstats['extra_exp_pts']     
    player_rating.save()
    player_obj.save()    
    return playerstats
    
def db_create_botrequest(player_id, action, common=0, uncommon=0, rare=0):
    request = BotRequest()
    request.player = Player.objects.get(id__exact=player_id)
    request.action = action
    request.status = 0
    request.common = common
    request.uncommon = uncommon
    request.rare = rare
    request.save()
    return request
    
    
def action_check_user_skill(steamid):
    # check your friends rating. It automatically creates
    # a new Database record for this guy.
    vapi = ValveApiWrapper.ValveApi()  
    try: 
        player = Player.objects.get(uid=steamid)
    except Player.DoesNotExist:
        player = db_create_player(steamid)                
    action_refresh_user_rating({'steamid':steamid})
    
    
def action_login(data):        
    # check if player is on ICL already.    
    # otherwise create a new record
    try: 
        player = Player.objects.get(uid=data['steamid'])
    except Player.DoesNotExist:
        player = db_create_player(data['steamid'])            
        if DEBUG: print "New player created"
        player.uid      = data['steamid']
        player.nickname = data['personaname']
        player.avatar   = data['social_auth'].extra_data.get('avatar')
        player.mumble_nickname = snippets.escape_username(data['personaname'])
        
    player.save()
 
 
def action_refresh_user_rating(data):
    player = Player.objects.get(uid=data['steamid'])
    # Unless the user has zero rating
    if player.rating.skillrating == 0:
        db_refresh_player_rating(data['steamid'])
        if DEBUG: print "OK"
    else:  
        # Ratings could only be updated once a day
        if player.rating.last_updated<=timezone.now()-timedelta(days=1):
          db_refresh_player_rating(data['steamid'])
          if DEBUG: print "OK"
        else:
          if DEBUG: print "Refreshing only allowed once a day"
        
        
        
        
        
        
        
        
        
        
def action_inventory_add_items(steamid):
    # User wants to put new items in his inventory
    player_id = Player.objects.get(uid=steamid).id
    db_create_botrequest(player_id, 0)
    
def action_inventory_take_items(steamid):
    # User wants to take some items from his inventory
    player = Player.objects.get(uid=steamid)
    player_id = player.id
    
    common   = 0
    uncommon = 0
    rare     = 0
    
    # Only give 30 items max per day
    if player.inventory.rare >= 10:
        rare = 10
    else:
        rare = player.inventory.rare
        
    if player.inventory.uncommon >= 10:
        uncommon = 10
    else:
        uncommon = player.inventory.uncommon        
        
    if player.inventory.common >= 10:
        common = 10    
    else:
        common = player.inventory.common
        
    # You can only perform one take items action a day
    if BotRequest.objects.filter(last_updated__gte=timezone.now()-timedelta(days=1), player__id__exact=player_id, action__exact=1).count() == 0:
      db_create_botrequest(player_id, 1, common, uncommon, rare)
      if DEBUG: print "OK"
    else:
      if DEBUG: print "You can only take back items once a day"
    

    