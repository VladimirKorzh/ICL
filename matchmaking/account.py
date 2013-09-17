from matchmaking.models import Player, Inventory, Rating, BotRequest
import ValveApiWrapper

from datetime import timedelta
from django.utils import timezone

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
    
def db_refresh_player_rating(steamid):
    vapi = ValveApiWrapper.ValveApi()
    player_obj    = Player.objects.get(uid=steamid)
    player_rating = player_obj.rating    
    
    playerstats = vapi.get_player_exp_from_steamid(steamid)  
    
    player_obj.nickname       = playerstats['nickname']    
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
    
def action_refresh_user_stats(steamid):
    # user wants to know his friends skill level
    # or skill of any user that has never been to ICL
    # it automatically registers user in Database    
        
    # check if player is on ICL already.    
    try: 
        player = Player.objects.get(uid=steamid)
    except Player.DoesNotExist:
        player = db_create_player(steamid)
  
    # Unless the user has zero rating
    if player.rating.skillrating == 0:
        db_refresh_player_rating(steamid)
    else:  
        # Ratings could only be updated once a day
        if player.rating.last_updated<=timezone.now()-timedelta(days=1):
          db_refresh_player_rating(steamid)
        
def action_inventory_add_items(steamid):
    # User wants to put new items in his inventory
    player_id = Player.objects.get(uid=steamid).id
    db_create_botrequest(player_id, 0)
    
def action_inventory_take_items(steamid, common, uncommon, rare):
    # User wants to take some items from his inventory
    player_id = Player.objects.get(uid=steamid).id
    
    # You can only perform one take items action a day
    if BotRequest.objects.filter(last_updated__gte=timezone.now()-timedelta(days=1), player__id__exact=player_id, action__exact=1).count() == 0:
      db_create_botrequest(player_id, 1, common, uncommon, rare)    
    
    
    